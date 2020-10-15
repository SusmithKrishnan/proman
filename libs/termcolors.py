class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BRIGHT_WHITE = '\u001b[37;1m'
    GREY = '\033[38;5;240m'


def bold(st):
    return(color.BOLD + str(st)+color.END)


def grey(st):
    return(color.GREY + str(st)+color.END)
