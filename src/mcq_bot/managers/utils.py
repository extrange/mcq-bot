from typing import Callable, Concatenate

from mcq_bot.db.connection import get_engine
from sqlalchemy.orm import Session


# TODO make the order of with_session arbitrary
def with_session[**P, R, C](func: Callable[Concatenate[C, Session, P], R]):
    """
    Wrap a classmethod with a Session instance, providing the Session as the first argument.

    Must be called after `@classmethod`.

    Usage:

    ```python
    @classmethod
    @with_session
    def my_class_method(cls, s: Session, arg1, ...): ...
    ```
    """

    def wrap(_class: C, *args: P.args, **kwargs: P.kwargs) -> R:
        with Session(get_engine(), expire_on_commit=False) as s:
            return func(_class, s, *args, **kwargs)

    return wrap
