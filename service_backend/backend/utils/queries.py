"""Module with tools to unify query common operations."""
import functools
import flask_smorest


def to_pagination():
    """Decorator to convert the result query into a pagination object.

    :return: Decorated function
    :rtype: fun
    """
    def decorator_add_sorting(func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            """Converts the query into a pagination object."""
            query_args = args[1]
            per_page = query_args.pop('per_page')
            page = query_args.pop('page')
            query = func(*args, **kwargs)
            return query.paginate(page, per_page)
        return decorator
    return decorator_add_sorting


def add_sorting(model):
    """Decorator to add sorting functionality to a controller method.

    :param model: Model with containing the sorting field
    :type model: :class:`backend.model.core.BaseModel`
    :return: Decorated function
    :rtype: fun
    """
    def decorator_add_sorting(func):
        @functools.wraps(func)
        def decorator(*args, **kwargs):
            """Returns a sorting sql object from a model and a field control.
            The field must be preceded with a control character:
            - '+' return an ascending sort object
            - '-' return a descending sort object
            """
            query_args = args[1]
            sort_by = query_args.pop('sort_by')
            sort_by = sort_by if sort_by != None else ""
            query = func(*args, **kwargs)
            sorting = [parse_sort(model, x) for x in sort_by.split(',') if x != ""]
            return query.order_by(*sorting)
        return decorator
    return decorator_add_sorting


def parse_sort(model, control_field):
    try:
        field = model.__dict__[control_field[1:]]
        operator = control_field[0]
    except KeyError as err:
        flask_smorest.abort(422, message={
            'KeyError': f"Unexpected field '{err.args[0]}'",
            'hint': "Use ',' to separate fields",
            'possible_fields': [x.name for x in model.__table__.columns]
        })
    if operator == '+':
        return field.asc()
    if operator == '-':
        return field.desc()
    else:
        flask_smorest.abort(422, message={
            'KeyError': f"Unknown order operator '{operator}'",
            'hint': "Use '+'(asc) or '-'(desc) before sort field"
        })
