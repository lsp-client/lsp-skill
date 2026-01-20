from pydantic import RootModel


class Nullable[T](RootModel[T | None]):
    root: T | None
