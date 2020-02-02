# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re

regex = r"(\d*)[\.\,]?(\d*)"
p = re.compile(regex)

test_strings = [
    "€54,95",
    "€54.95",
    "  €50",
    "54,95€",
    "54.95€",
    "  50€",
    "54,95",
    "239.95",
    "54.95",
]

def StringToCurrency(test_str):
    s = re.sub(r"\s\s+", " ", test_str)
    s = s.replace(",", ".")
    s = s.replace("€", "")
    s = s.replace("$", "")
    try:
        f = float(s)
        return f
    except ValueError:
        return float('nan')

if __name__ == "__main__":
    for test_str in test_strings:
        print(f"{test_str} ->{StringToCurrency(test_str)}")
