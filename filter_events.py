# -*- coding: utf-8 -*-
"""Печатает события уровня critical из events.json."""

import json
import sys
from pathlib import Path


def main():
    events = json.loads(Path("events.json").read_text(encoding="utf-8"))
    critical = filter(lambda item: item["level"].casefold() == "critical", events)
    count = 0
    for item in critical:
        print(item["event"])
        count += 1
    print("критичных %d" % count)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    main()
