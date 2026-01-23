from lsap.schema.locate import LineScope, SymbolScope


def parse_scope(scope_str: str | None) -> LineScope | SymbolScope | None:
    """
    Parse a scope string into LineScope or SymbolScope.

    Scope formats:
        - <line> - Single line number (e.g., "42")
        - <start>,<end> - Line range with comma (e.g., "10,20"). Use 0 for end to mean till EOF (e.g., "10,0")
        - <symbol_path> - Symbol path with dots (e.g., "MyClass.my_method")
    """
    if not scope_str:
        return None

    if "," in scope_str:
        start, end = scope_str.split(",", 1)
        return LineScope(start_line=int(start), end_line=int(end))

    if scope_str.isdigit():
        start_line = int(scope_str)
        return LineScope(start_line=start_line, end_line=start_line + 1)

    symbol_path = scope_str.split(".")
    return SymbolScope(symbol_path=symbol_path)
