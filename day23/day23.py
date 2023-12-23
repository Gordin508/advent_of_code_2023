import logging
from enum import Enum
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TileType(Enum):
    PATH = 1,
    FOREST = 2,
    UPSLOPE = 3,
    DOWNSLOPE = 4,
    LEFTSLOPE = 5,
    RIGHTSLOPE = 6

    @classmethod
    def from_int(cls, value):
        for member in cls:
            if member.value == value:
                return member

    @classmethod
    def from_letter(cls, letter):
        if letter == '.':
            return cls.PATH
        elif letter == '#':
            return cls.FOREST
        elif letter == '^':
            return cls.UPSLOPE
        elif letter == 'v':
            return cls.DOWNSLOPE
        elif letter == '<':
            return cls.LEFTSLOPE
        elif letter == '>':
            return cls.RIGHTSLOPE
        else:
            raise ValueError(f"Unknown letter {letter}")

    def __str__(self):
        if self == self.PATH:
            return '.'
        elif self == self.FOREST:
            return '#'
        elif self == self.UPSLOPE:
            return '^'
        elif self == self.DOWNSLOPE:
            return 'v'
        elif self == self.LEFTSLOPE:
            return '<'
        elif self == self.RIGHTSLOPE:
            return '>'
        else:
            raise ValueError(f"Unknown TileType {self}")


class Node:
    def __init__(self, y, x):
        self.neighbors = set()
        self.y = y
        self.x = x

    def addNeighbor(self, node):
        if node is None:
            return
        self.neighbors.add(node)
        node.neighbors.add(self)

    def getNeighbors(self):
        return self.neighbors

    def numNeighbors(self):
        return len(self.neighbors)

    def distance(self, other):
        assert self.y == other.y or self.x == other.x
        return abs(self.y - other.y) + abs(self.x - other.x)

    def __eq__(self, other):
        return self.y == other.y and self.x == other.x

    def __hash__(self):
        # only hash y and x coordinate
        return hash((self.y, self.x))


class HikingMap:
    def __init__(self, lines):
        self.height = len(lines)
        self.width = len(lines[0].strip())
        self.grid = np.zeros((self.height, self.width), dtype=object)
        for y, line in enumerate(lines):
            for x, letter in enumerate(line.strip()):
                self.grid[y, x] = TileType.from_letter(letter)
        self.distances = None
        self.start = next(((0, x) for x in range(self.width) if self.grid[0, x] == TileType.PATH))
        self.dest = next(((self.height - 1, x) for x in range(self.width) if self.grid[self.height - 1, x] == TileType.PATH))

    def _buildCompressedGraph(self):
        from itertools import product
        self.nodes = {(y, x): Node(y, x) for (y, x) in product(range(self.height), range(self.width)) if self.grid[y,x] != TileType.FOREST}
        for node in self.nodes:
            y = node.y
            x = node.x
            for coord in [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]:
                node.addNeighbor(self.nodes.get((y, x)), None)

        # zap unneeded nodes
        pass

    def calculateLongestDistances(self, part2=False):
        if self.distances is not None:
            return

        # we always store distance + 1 so we can abuse this as visited map also
        visited = np.zeros(self.grid.shape, dtype=np.int8)
        start_time = np.zeros(self.grid.shape, dtype=np.uint32)
        end_time = np.zeros(self.grid.shape, dtype=np.uint32)

        def neighbors(y, x):
            if not part2:
                ttype = self.grid[y, x]
                if ttype == TileType.DOWNSLOPE and y < self.height - 1:
                    yield ((y + 1, x))
                if ttype == TileType.UPSLOPE and y > 0:
                    yield ((y - 1, x))
                if ttype == TileType.LEFTSLOPE and x > 0:
                    yield ((y, x - 1))
                if ttype == TileType.RIGHTSLOPE and x < self.width - 1:
                    yield ((y, x + 1))
                if ttype != TileType.PATH:
                    return

            if y > 0:
                yield ((y - 1, x))
            if y < self.height - 1:
                yield ((y + 1, x))
            if x > 0:
                yield ((y, x - 1))
            if x < self.width - 1:
                yield ((y, x + 1))

        # DFS
        stack = [(*self.start, 0)]
        time = 0
        maxpathlen = 0

        while stack:
            time += 1
            y, x, d = stack.pop()
            if not visited[y, x]:
                visited[y, x] = 1
                stack.append((y, x, d))  # for backtracking
                start_time[y, x] = time
                # add all edges
                if (y, x) == self.dest:
                    maxpathlen = max(maxpathlen, d)
                    continue
                for ny, nx in neighbors(y, x):
                    ntype = self.grid[ny, nx]
                    if ntype == TileType.FOREST:
                        continue
                    if not visited[ny, nx]:
                        stack.append((ny, nx, d + 1))

            elif end_time[y, x] == 0:
                # backtrack
                end_time[y, x] = time
                visited[y, x] = 0
        return maxpathlen

    def __str__(self):
        return '\n'.join(''.join(str(x) for x in row) for row in self.grid)


def part1(lines):
    import ipdb; ipdb.set_trace()
    hikingmap = HikingMap(lines)
    return hikingmap.calculateLongestDistances()


def part2(lines):
    hikingmap = HikingMap(lines)
    return hikingmap.calculateLongestDistances(part2=True)


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
