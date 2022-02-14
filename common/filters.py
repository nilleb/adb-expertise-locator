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


def should_exclude_keyword(keyword):
    return "adb" in keyword or "ta " in keyword or "rrp" in keyword or keyword in USELESS_KEYWORDS


USELESS_KEYWORDS = set(
    [
        # "adb rrp report recommendation president",
        # "adb technical assistance ta report",
        "tar",
        "approved technical assistance",
        # "ta projects",
        # "adb technical assistance",
        "recommendations of the president",
        "board approval",
        "approved projects",
        "terms and conditions",
        "rrp",
        # "adb project",
        # "adb projects",
        # "adb regional technical assistance",
        # "adb cdta",
        # "adb covid-19 response",
        # "adb loans",
        # "adb rrp report recommendation president results based lending",
        "report and recommendation of the president",
        "technical assistance",
        "asian development bank",
        "report recommendation president",
        # "ta report",
        # "rrp linked document",
    ]
)
