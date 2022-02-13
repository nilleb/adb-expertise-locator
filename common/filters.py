from operator import countOf


def is_valid_author_name(fullname):
    return (
        len(fullname) < 50
        and countOf(fullname, " ") < 5
        and countOf(fullname, ".") < 5
        and " " in fullname
    )


def strip_unwanted(title):
    return title.replace(": Report and Recommendation of the President", "")


def should_be_downloaded(url):
    return "rrp" in url or "tar" in url
