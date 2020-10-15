import string

def check_hex(val):
    for letter in val:
        if letter not in string.hexdigits:
            return False
    return True
