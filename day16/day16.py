import logging
import numpy as np
from enum import Enum, Flag, auto

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Beamdirection(Flag):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def walk(self, y, x):
        # walk in direction on coords
        if self == Beamdirection.UP:
            return y - 1, x
        elif self == Beamdirection.DOWN:
            return y + 1, x
        elif self == Beamdirection.LEFT:
            return y, x - 1
        elif self == Beamdirection.RIGHT:
            return y, x + 1
        else:
            raise ValueError(f"Unexpected direction {self}")

    def split(self):
        if self == Beamdirection.UP or self == Beamdirection.DOWN:
            return (Beamdirection.LEFT, Beamdirection.RIGHT)
        else:
            return (Beamdirection.UP, Beamdirection.DOWN)

    def reflect(self, mirror: str):
        assert mirror in ["/", "\\"]
        if (self == Beamdirection.RIGHT and mirror == "/") or (self == Beamdirection.LEFT and mirror == "\\"):
            return Beamdirection.UP
        if (self == Beamdirection.RIGHT and mirror == "\\") or (self == Beamdirection.LEFT and mirror == "/"):
            return Beamdirection.DOWN
        if (self == Beamdirection.UP and mirror == "\\") or (self == Beamdirection.DOWN and mirror == "/"):
            return Beamdirection.LEFT
        if (self == Beamdirection.UP and mirror == "/") or (self == Beamdirection.DOWN and mirror == "\\"):
            return Beamdirection.RIGHT
        assert False, f"Something went wrong: {self}, {mirror}"

    def tochar(self):
        chars = []
        if Beamdirection.UP in self:
            chars.append("^")
        if Beamdirection.DOWN in self:
            chars.append("v")
        if Beamdirection.LEFT in self:
            chars.append("<")
        if Beamdirection.RIGHT in self:
            chars.append(">")
        if len(chars) == 0:
            return "."
        elif len(chars) == 1:
            return chars[0]
        else:
            return str(len(chars))


def calcenergy(directions, printout=False):
    height = len(directions)
    width = len(directions[0])
    energized = np.zeros((height, width), dtype=np.int8)
    for y in range(height):
        for x in range(width):
            energized[y, x] = 1 if directions[y][x] is not None else 0

    if printout:
        for y in range(height):
            for x in range(width):
                if energized[y, x] == 1:
                    print('#', end='')
                else:
                    print('.', end='')
            print('')
    return energized


def printdirections(directions, grid):
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] != ".":
                print(grid[y][x], end='')
            else:
                print(directions[y][x].tochar() if directions[y][x] is not None else grid[y][x], end='')


def part1(lines):
    height = len(lines)
    width = len(lines[0].strip())
    grid = lines
    directions = [[None for _ in range(width)] for _ in range(height)]

    queue = []
    # first step is always top left tile

    def enqueue(q, y, x, indirection: Beamdirection):
        if 0 > y or y >= height:
            return
        if 0 > x or x >= width:
            return

        currentdir = directions[y][x]
        if currentdir is None:
            directions[y][x] = indirection
        elif indirection in currentdir:
            # already in queue or treated
            return
        directions[y][x] |= indirection
        q.append((y, x, indirection))

    enqueue(queue, 0, 0, Beamdirection.RIGHT)

    # import ipdb; ipdb.set_trace()
    while len(queue) > 0:
        newqueue = []
        for y, x, direction in queue:
            match (grid[y][x]):
                case '.':
                    # go further in direction
                    yn, xn = direction.walk(y, x)
                    enqueue(newqueue, yn, xn, direction)
                case '-':
                    if direction == Beamdirection.LEFT or direction == Beamdirection.RIGHT:
                        yn, xn = direction.walk(y, x)
                        enqueue(newqueue, yn, xn, direction)
                    else:
                        split = direction.split()
                        for splitdir in split:
                            yn, xn = splitdir.walk(y, x)
                            enqueue(newqueue, yn, xn, splitdir)
                case '|':
                    if direction == Beamdirection.UP or direction == Beamdirection.DOWN:
                        yn, xn = direction.walk(y, x)
                        enqueue(newqueue, yn, xn, direction)
                    else:
                        split = direction.split()
                        for splitdir in split:
                            yn, xn = splitdir.walk(y, x)
                            enqueue(newqueue, yn, xn, splitdir)
                case '\\' | '/':
                    newdir = direction.reflect(grid[y][x])
                    yn, xn = newdir.walk(y, x)
                    enqueue(newqueue, yn, xn, newdir)
                case _:
                    assert False, f"{grid[y][x]}"
        queue = newqueue

    energized = calcenergy(directions)
    return np.sum(energized)


def part2(lines):
    height = len(lines)
    width = len(lines[0].strip())
    grid = lines
    directions = [[None for _ in range(width)] for _ in range(height)]

    queue = []
    # first step is always top left tile

    def enqueue(q, y, x, indirection: Beamdirection):
        if 0 > y or y >= height:
            return
        if 0 > x or x >= width:
            return

        currentdir = directions[y][x]
        if currentdir is None:
            directions[y][x] = indirection
        elif indirection in currentdir:
            # already in queue or treated
            return
        directions[y][x] |= indirection
        q.append((y, x, indirection))

    combinations = [(y, 0, Beamdirection.RIGHT) for y in range(height)]
    combinations += [(y, width - 1, Beamdirection.LEFT) for y in range(height)]
    combinations += [(0, x, Beamdirection.DOWN) for x in range(width)]
    combinations += [(height - 1, x, Beamdirection.UP) for x in range(width)]
    record = 0
    for starty, startx, startdir in combinations:
        directions = [[None for _ in range(width)] for _ in range(height)]

        queue = []
        # test all possible left/right injections

        enqueue(queue, starty, startx, startdir)

        # import ipdb; ipdb.set_trace()
        while len(queue) > 0:
            newqueue = []
            for y, x, direction in queue:
                match (grid[y][x]):
                    case '.':
                        # go further in direction
                        yn, xn = direction.walk(y, x)
                        enqueue(newqueue, yn, xn, direction)
                    case '-':
                        if direction == Beamdirection.LEFT or direction == Beamdirection.RIGHT:
                            yn, xn = direction.walk(y, x)
                            enqueue(newqueue, yn, xn, direction)
                        else:
                            split = direction.split()
                            for splitdir in split:
                                yn, xn = splitdir.walk(y, x)
                                enqueue(newqueue, yn, xn, splitdir)
                    case '|':
                        if direction == Beamdirection.UP or direction == Beamdirection.DOWN:
                            yn, xn = direction.walk(y, x)
                            enqueue(newqueue, yn, xn, direction)
                        else:
                            split = direction.split()
                            for splitdir in split:
                                yn, xn = splitdir.walk(y, x)
                                enqueue(newqueue, yn, xn, splitdir)
                    case '\\' | '/':
                        newdir = direction.reflect(grid[y][x])
                        yn, xn = newdir.walk(y, x)
                        enqueue(newqueue, yn, xn, newdir)
                    case _:
                        assert False, f"{grid[y][x]}"
            queue = newqueue

        energized = calcenergy(directions)
        energy = np.sum(energized)
        if energy > record:
            record = energy
    return record


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
