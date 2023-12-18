import logging
import re
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LINEREGEX = re.compile(r"(?P<direction>[UDLR])\s+(?P<distance>\d+)\s+\(\#(?P<rgb>[0-9a-f]{6})\)")


class Command:
    def __init__(self, direction: str, distance: int, rgb: str):
        assert direction in 'UDLR'
        assert distance >= 1
        self.direction = direction
        self.distance = distance
        self.rgb = rgb

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
        position = (0, 0)
        minx, miny, maxx, maxy = 0, 0, 0, 0
        self.commands = commands

        def updatemax(position):
            nonlocal minx, miny, maxx, maxy
            minx = min(position[1], minx)
            miny = min(position[0], miny)
            maxx = max(position[1], maxx)
            maxy = max(position[0], maxy)

        for command in commands:
            newy, newx = position
            match command.direction:
                case "U":
                    newy -= command.distance
                case "D":
                    newy += command.distance
                case "L":
                    newx -= command.distance
                case "R":
                    newx += command.distance
                case _:
                    assert False, f"{command}"
            position = (newy, newx)
            updatemax(position)

        height = maxy - miny + 1
        width = maxx - minx + 1
        grid = np.zeros((height, width), dtype=np.int8)
        self.grid = grid
        position = (0 - miny, 0 - minx)
        startpos = position
        for command in commands:
            oldx, oldy = position[1], position[0]
            newx, newy = oldx, oldy
            match command.direction:
                case "U":
                    newy -= command.distance
                case "D":
                    newy += command.distance
                case "L":
                    newx -= command.distance
                case "R":
                    newx += command.distance
                case _:
                    assert False, f"{command}"
            position = (newy, newx)
            if newx < oldx:
                newx, oldx = oldx, newx
            if newy < oldy:
                newy, oldy = oldy, newy
            for y in range(oldy, newy + 1):
                for x in range(oldx, newx + 1):
                    grid[y, x] = 1
        assert position == startpos, f"{position} {startpos}"
        self.grid = grid

    def calculateInside(self):
        # shoelace
        result = 0
        bordersum = 0
        position = Position(0, 0)
        # shoelace formula + pick's theorem
        for i in range(len(self.commands)):
            c1 = self.commands[i]
            c2 = self.commands[(i + 1) % len(self.commands)]
            p1 = position + c1
            p2 = p1 + c2
            result += p1.x * p2.y - p1.y * p2.x
            bordersum += (p1 - p2).abs()
            position = p1
        result = (abs(result) + bordersum) // 2 + 1
        return result

    def printgrid(self):
        for line in self.grid:
            print("".join(('.' if x == 0 else '#' for x in line)))


def part1(lines):
    import ipdb; ipdb.set_trace()
    commands = []
    for line in lines:
        # parse input
        match = LINEREGEX.match(line.strip())
        direction, distance, rgb = match['direction'], int(match['distance']), match['rgb']
        commands.append(Command(direction, distance, rgb))

    grid = Grid(commands)
    grid.printgrid()
    return grid.calculateInside()


def part2(lines):
    raise NotImplementedError("Part 2 not yet implemented")


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
