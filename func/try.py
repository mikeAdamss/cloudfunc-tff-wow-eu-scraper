
import re

# TODO, use a regular expressions ffs
patterns = [
    "<span title=Jan",
    "<span title=Feb",
    "<span title=Mar",
    "<span title=Apr",
    "<span title=May",
    "<span title=Jun",
    "<span title=Jul",
    "<span title=Aug",
    "<span title=Sep",
    "<span title=Oct",
    "<span title=Nov",
    "<span title=Dec"
    ]


if re.match(pattern, "<span title=Jain"):
    print("matches")
