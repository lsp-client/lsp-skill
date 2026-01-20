from attrs import define


@define
class State:
    debug: bool = False
    "Enable verbose debug logging for troubleshooting."


state = State()
