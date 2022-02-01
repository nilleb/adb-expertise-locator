from operator import countOf

def is_valid_author_name(fullname):
    return (
        len(fullname) < 50
        and countOf(fullname, " ") < 5
        and countOf(fullname, ".") < 5
        and " " in fullname
    )
