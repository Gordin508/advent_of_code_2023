import logging
import re
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LINEREGEX = re.compile(r"(?P<direction>[UDLR])\s+(?P<distance>\d+)\s+\(\#(?P<rgb>[0-9a-f]{6})\)")


class Command:
    def __init__(self, direction: str, distance: int, rgb: str, part2=False):
        assert direction in 'UDLR'
        assert distance >= 1
        self.direction = direction
        self.distance = distance
        self.rgb = rgb

        if part2:
            self.distance = int(self.rgb[:5], 16)
            match int(self.rgb[-1]):
                case 0:
                    self.direction = "R"
                case 1:
                    self.direction = "D"
                case 2:
                    self.direction = "L"
                case 3:
                    self.direction = "U"

    def __str__(self):
        return f"{self.direction} {self.distance} (#{self.rgb})"

    def __repr__(self):
        return self.__str__()


class Position:
    def __init__(self, y, x):
        self.y = y
        self.x = x

    def __add__(self, other):
        if isinstance(other, type(self)):
            return type(self)(self.y + other.y, self.x + other.x)
        elif isinstance(other, Command):
            newx = self.x
            newy = self.y
            match (other.direction):
                case 'U':
                    newy -= other.distance
                case 'D':
                    newy += other.distance
                case 'L':
                    newx -= other.distance
                case 'R':
                    newx += other.distance
            return type(self)(newy, newx)
        else:
            assert False

    def __sub__(self, other):
        assert isinstance(other, type(self))
        return type(self)(self.y - other.y, self.x - other.x)

    def abs(self):
        return abs(self.x) + abs(self.y)

    def __str__(self):
        return f"{self.y} {self.x}"

    def __repr__(self):
        return self.__str__()


class Grid:
    def __init__(self, commands: [Command]):
        self.commands = commands

    def calculateInside(self):
        # shoelace formula + pick's theorem
        inner = 0  # inner area
        borderpoints = 0  # note: original (0, 0) position is included in last edge
        position = Position(0, 0)  # commands are relative, so we need this for bookkeeping
        for i in range(len(self.commands)):
            c1 = self.commands[i]
            c2 = self.commands[(i + 1) % len(self.commands)]
            p1 = position + c1
            p2 = p1 + c2
            inner += p1.x * p2.y - p1.y * p2.x
            borderpoints += (p1 - p2).abs()  # length of edge from p1 to p2 (excluding starting point)
            position = p1
        inner = (abs(inner) + borderpoints) // 2 + 1  # + 1 instead of -1 due to the nature of our grid
        return inner


def part1(lines):
    commands = []
    for line in lines:
        # parse input
        match = LINEREGEX.match(line.strip())
        direction, distance, rgb = match['direction'], int(match['distance']), match['rgb']
        commands.append(Command(direction, distance, rgb))

    grid = Grid(commands)
    return grid.calculateInside()


def part2(lines):
    commands = []
    for line in lines:
        # parse input
        match = LINEREGEX.match(line.strip())
        direction, distance, rgb = match['direction'], int(match['distance']), match['rgb']
        commands.append(Command(direction, distance, rgb, part2=True))

    grid = Grid(commands)
    return grid.calculateInside()


def main():
    import sys
    import os
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    if not os.path.isfile(infile):
        logger.error(f"Input file {infile} does not exist")
        return

    with open(infile) as f:
        lines = f.readlines()

    for i, fun in enumerate((part1, part2), start=1):
        try:
            result = fun(lines)
        except NotImplementedError as e:
            logger.debug(e)
            continue
        if result is None:
            logger.error(f"Part {i} does not return a result")
            continue
        logger.info(f"Part {i}: {result}")


if __name__ == '__main__':
    main()
