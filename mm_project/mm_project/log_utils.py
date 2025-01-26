from terminology import in_red, in_bold, in_green


def write_error_log(title: str, message: str):
    print(
        in_bold(title),
        in_red(message),
        sep=':'
    )

def write_log(title: str, message: str):
    print(
        in_bold(title),
        in_green(message),
        sep=':'
    )
