from typing import Callable

from functools import wraps
from inspect import iscoroutinefunction, signature

from tortoise.transactions import in_transaction


def transaction(func: Callable):
    if not iscoroutinefunction(func):
        raise TypeError("transaction decorator only supports async functions")

    sig = signature(func)
    conn_param = sig.parameters.get("connection")
    if conn_param is None:
        raise TypeError("wrapped function must accept a 'connection' parameter")

    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "connection" in kwargs and kwargs["connection"] is not None:
            return await func(*args, **kwargs)

        async with in_transaction() as conn:
            return await func(*args, connection=conn, **kwargs)
    return wrapper        
    