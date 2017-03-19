class ModelFieldMissingError(Exception):
    pass


class ModelFieldReadOnlyError(Exception):
    pass


class ModelSessionBlogLockedError(Exception):
    pass


class ModelSessionReadOnlyError(Exception):
    pass


class ModelInvalidError(Exception):
    def __init__(self, model, fmt, **kw):
        self._model = model
        self._err = fmt.format(**kw)

    def __str__(self):
        res = '{clsname}'.format(clsname=self._model.__class__.__name__)
        if hasattr(self._model, 'uuid'):
            res += ' uuid={uuid}'.format(uuid=self._model.uuid)
        res += ': {err}'.format(err=self._err)
        return res


class ModelFieldBoolOpError(Exception):
    pass


class ModelQueryError(Exception):
    pass


class ModelQueryNoObjectFoundError(ModelQueryError):
    pass


class ModelQueryTooManyObjectsError(ModelQueryError):
    pass


class ModelQueryInvalidCriterionError(ModelQueryError):
    pass


class ModelQueryParentAlreadySetError(ModelQueryError):
    pass


class ModelQueryNoParentError(ModelQueryError):
    pass


class ModelQueryParentWrongTypeError(ModelQueryError):
    pass