from typing import Any

from starlette_context.ctx import _Context, context


class TypedContext(_Context):
    language: str

    def __getattr__(self, name: str) -> Any:
        return context.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        context[name] = value


ctx = TypedContext()
