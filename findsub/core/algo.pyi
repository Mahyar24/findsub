from datetime import timedelta

def match(
    base: list[tuple[timedelta, timedelta]], other: list[tuple[timedelta, timedelta]]
) -> float: ...
