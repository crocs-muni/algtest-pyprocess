def null_if_none(x: any):
    return 'null' if x is None else x


def bool_to_tf(x: bool) -> str:
    return 'true' if x else 'false'
