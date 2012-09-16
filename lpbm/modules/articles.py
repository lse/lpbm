# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import datetime
import os
import subprocess
import sys

import lpbm.datas.articles
import lpbm.logging
import lpbm.module_loader
import lpbm.path

_LOGGER = lpbm.logging.get()

class Articles(lpbm.module_loader.Module):
    def name(self): return 'articles'
    def abstract(self): return 'Loads, manipulates and renders articles.'

    def init(self):
        self.parser.add_argument('-i', '--id', action='store', type=int,
                                 metavar='id', default=None,
                                 help='Selects an article for several options.')

        group = self.parser.add_argument_group(title='general actions')
        group.add_argument('-n', '--new', action='store', metavar='filename',
                           help='Help create a new draft. ' + \
                                '(path/to/articles/ARGUMENT.markdown)')
        group.add_argument('-l', '--list', action='store_true',
                           help='List all the articles.')

        group = self.parser.add_argument_group(
            title='specific actions (need --id)'
        )
        group.add_argument('-p', '--publish', action='store_true',
                           help='Publishes the draft.')
        group.add_argument('-P', '--preview', action='store_true',
                           help='Only renders draft articles.')
        group.add_argument('-e', '--edit', action='store_true',
                           help='Opens your $EDITOR on the article.')

    def load(self, modules, args):
        self.articles, f = dict(), lambda a: a.endswith('.markdown')
        for f in lpbm.path.filter_files(f, self.args.exec_path, 'articles'):
            art = lpbm.datas.articles.Article(f)
            self.articles[art.id] = art

    def process(self, modules, args):
        if args.list:
            self.list_articles()
            return
        elif args.new:
            self.new_article(args.new)
            return

        if args.id is None:
            self.parser.error('This action needs --id option.')
        elif args.publish:
            self.publish_article(args.id)
        elif args.preview:
            self.preview_article(args.id)
        elif args.edit:
            self.edit_article(args.id)

    # Particular functions for command line.
    def list_articles(self):
        count, count_pub = 0, 0
        print('All articles:')
        for article in self.articles.values():
            print(' {id:2d} + "{title}" by {authors} [{published}]'.format(
                id = article.id, title = article.title,
                authors = article.authors_list(),
                published = 'published' if article.published else 'draft',
            ))
            count += 1
            if article.published:
                count_pub += 1
        print('    + {} article(s) available ({} published, {} drafts).'.format(
            count, count_pub, count - count_pub
        ))

    def publish_article(self, id):
        try:
            article = self.articles[id]
            article.publish()
            article.save()
            print('Article "{title}" by {authors} was published.'.format(
                title = article.title,
                authors = article.authors_list(),
            ))
        except KeyError:
            sys.exit('This article doesn\'t exist.')

    def preview_article(self, id):
        self.check_article_selected('preview')
        # FIXME

    def new_article(self, filename):
        # First we check that file doesn't exist.
        path = lpbm.path.join(
            self.args.exec_path, 'articles', '{}.markdown'.format(filename)
        )
        if os.path.exists(path):
            sys.exit('File `{}\' exists, please choose a different name.'.format(
                path
            ))
        # Then we check if we want to use the first available id.
        ids, pk = self.articles.keys(), None
        try:
            last_id = max(ids) + 1
        except ValueError:
            last_id = 0
        while pk is None:
            try:
                pk = int(input('Please enter an id [{}]: '.format(last_id)))
                if pk in ids:
                    print('Id already exists, please choose a different one.')
                    pk = None
            except ValueError:
                pk = last_id

        # Then we want a title.
        title = input('Please enter a title: ')
        authors = input('Please list authors (comma separated): ')
        article = lpbm.datas.articles.Article(path)
        article.id = pk
        article.title = title
        article.add_authors(authors)
        article.save()
        self.articles[article.id] = article

        # We successfully created article.
        print('Article `{}\' was successfully created!'.format(path))

        # Why not edit right away?
        edit = input('Do you want to edit this article right now? [y/N] ')
        if edit.lower() == 'y':
            self.edit_article(article.id)

    def edit_article(self, id):
        try:
            article = self.articles[id]
        except KeyError:
            sys.exit('This article doesn\'t exist.')
        subprocess.call('{editor} "{filename}"'.format(
            editor = os.environ.get('EDITOR', 'vim'),
            filename = article.path,
        ), shell=True)
