#!/usr/bin/env python3

import sys
import re
from collections import namedtuple, defaultdict

RGB = namedtuple('RGB', ['r', 'g', 'b'])
GAMEREGEX = r"Game (?P<game>\d+):(?P<draws>((\s\d+\s(?P<color>(red|green|blue)),?)+;?)+)"


def parsegame(line):
    line = line.strip()
    match = re.match(GAMEREGEX, line)
    gameid = int(match.group('game'))
    draws = match.group('draws').split(';')
    rgbs = []
    for draw in draws:
        draws_rgb = defaultdict(int)
        colors = draw.strip().split(',')
        for c in colors:
            colormatch = re.match(r"(?P<count>\d+)+\s(?P<color>(red|green|blue))", c.strip())
            draws_rgb[colormatch.group('color')] += int(colormatch.group('count'))
        rgbs.append(RGB(draws_rgb['red'], draws_rgb['green'], draws_rgb['blue']))

    return gameid, rgbs


def main():
    infile = "input.txt" if len(sys.argv) == 0 else sys.argv[-1]
    with open(infile, 'r') as f:
        lines = f.readlines()
    sum = 0

    def power(rgb):
        return rgb.r * rgb.g * rgb.b

    def minrgb(rgbs):
        return RGB(
            max((rgb.r for rgb in rgbs)),
            max((rgb.g for rgb in rgbs)),
            max((rgb.b for rgb in rgbs))
        )
    for line in lines:
        gameid, rgbs = parsegame(line)
        sum += power(minrgb(rgbs))

    print(sum)


if __name__ == "__main__":
    main()
