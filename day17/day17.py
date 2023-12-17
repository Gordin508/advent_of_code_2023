import logging
import numpy as np
import heapq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Direction:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        assert (abs(self.x) + abs(self.y)) == 1, f"{self.y} {self.x}"

    def __eq__(self, other):
        return self.y == other.y and self.x == other.x

    def __hash__(self):
        return hash((self.y, self.x))

    def __add__(self, other):
        return type(self)(self.y + other.y, self.x + other.x)

    def rotLeft(self):
        newy = 0 if self.y != 0 else (1 if self.x == -1 else -1)
        newx = 0 if self.x != 0 else (1 if self.y == 1 else -1)
        return type(self)(newy, newx)

    def rotRight(self):
        newy = 0 if self.y != 0 else (-1 if self.x == -1 else 1)
        newx = 0 if self.x != 0 else (-1 if self.y == 1 else 1)
        return type(self)(newy, newx)

    def __str__(self):
        return f"{self.y} {self.x}"

    def __repr__(self):
        return self.__str__()


class Position:
    def __init__(self, y, x):
        self.y = y
        self.x = x

    def __eq__(self, other):
        return self.y == other.y and self.x == other.x

    def __hash__(self):
        return hash((self.y, self.x))

    def __add__(self, other):
        return type(self)(self.y + other.y, self.x + other.x)

    def __str__(self):
        return f"{self.y} {self.x}"

    def __repr__(self):
        return self.__str__()


class State:
    def __init__(self, cost: int, position: Position, direction: Direction, count: int):
        self.cost = cost
        self.position = position
        self.direction = direction
        self.count = count

    def __lt__(self, other):
        return (self.cost, self.count) < (other.cost, other.count)

    def key(self):
        return (self.position, self.direction, self.count)

    def __str__(self):
        return f"{self.position} @cost {self.cost} in direction {self.direction} ({self.count})"

    def __repr__(self):
        return self.__str__()


def solve(grid, destination, minmove=0, maxmove=3):
    visited = set()
    queue = [State(0, Position(0, 0), Direction(1, 0), 0), State(0, Position(0, 0), Direction(0, 1), 0)]
    heapq.heapify(queue)

    def positionLegal(position):
        y, x = position.y, position.x
        return y >= 0 and y < grid.shape[0] and x >= 0 and x < grid.shape[1]

    while queue:
        nextnode = heapq.heappop(queue)
        if nextnode.key() in visited:
            continue
        visited.add(nextnode.key())
        if nextnode.position == destination and nextnode.count >= minmove:
            return nextnode.cost
        if not positionLegal(nextnode.position):
            continue
        newpos = nextnode.position + nextnode.direction
        if nextnode.count < maxmove and positionLegal(newpos):
            heapq.heappush(queue, State(nextnode.cost + grid[newpos.y, newpos.x], newpos, nextnode.direction, nextnode.count + 1))
        left = nextnode.direction.rotLeft()
        right = nextnode.direction.rotRight()
        if nextnode.count >= minmove:
            for x in (left, right):
                newpos = nextnode.position + x
                if positionLegal(newpos):
                    heapq.heappush(queue, State(nextnode.cost + grid[newpos.y, newpos.x], newpos, x, 1))

    assert False


def part1(lines):
    lines = [line.strip() for line in lines]
    height = len(lines)
    width = len(lines[0])
    grid = np.zeros((height, width), dtype=np.int8)
    for y, line in enumerate(lines):
        for x, number in enumerate(line):
            grid[y, x] = int(number)
    return solve(grid, destination=Position(height - 1, width - 1))


def part2(lines):
    lines = [line.strip() for line in lines]
    height = len(lines)
    width = len(lines[0])
    grid = np.zeros((height, width), dtype=np.int8)
    for y, line in enumerate(lines):
        for x, number in enumerate(line):
            grid[y, x] = int(number)
    return solve(grid, destination=Position(height - 1, width - 1), minmove=4, maxmove=10)


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
