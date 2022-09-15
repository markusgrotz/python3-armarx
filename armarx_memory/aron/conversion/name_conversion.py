import re


def snake_case_to_camel_case(name: str) -> str:
    # one_two_three to oneTwoThree
    # At each _, remove the _ and capitalize the following letter.
    tokens = name.split("_")
    out = tokens[0]
    out += "".join([s.capitalize() for s in tokens[1:]])

    return out


def camel_case_to_snake_case(name: str) -> str:
    # oneTwoThree to one_two_three
    regex = re.compile("[A-Z]")

    out = ""
    latest_end = 0

    for match in regex.finditer(name):
        out += (
            name[latest_end : match.start()]
            + "_"
            + name[match.start() : match.end()].lower()
        )
        latest_end = match.end()

    out += name[latest_end:]

    return out


if __name__ == "__main__":

    assert snake_case_to_camel_case("one_two_three") == "oneTwoThree"
    assert camel_case_to_snake_case("oneTwoThree") == "one_two_three"
