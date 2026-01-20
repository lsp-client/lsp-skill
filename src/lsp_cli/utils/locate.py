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

    # Check if it's a line scope (numeric formats)
    if "," in scope_str:
        # Comma-separated line range: "10,20"
        start, end = scope_str.split(",", 1)
        start_val = int(start)
        end_val = int(end)
        # 0 means till EOF, otherwise it's 1-based exclusive
        actual_end = 0 if end_val == 0 else end_val + 1
        return LineScope(start_line=start_val, end_line=actual_end)
    if scope_str.isdigit():
        # Single line number: "42"
        return LineScope(start_line=int(scope_str), end_line=int(scope_str) + 1)
    # Treat as symbol path
    symbol_path = scope_str.split(".")
    return SymbolScope(symbol_path=symbol_path)
