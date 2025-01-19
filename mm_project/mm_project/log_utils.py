from terminology import in_red, in_bold


def write_error_log(title: str, message: str):
    print(
        in_bold(title),
        in_red(message),
        sep=':'
    )
