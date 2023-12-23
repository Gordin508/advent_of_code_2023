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
        self.neighbors = {}
        self.y = y
        self.x = x

    def addNeighbor(self, node, distance=None):
        if node is None:
            return
        if node in self.neighbors:
            return
        if not distance:
            distance = self.distance(node)
        self.neighbors[node] = distance
        node.neighbors[self] = distance

    def getNeighbors(self):
        return self.neighbors.items()

    def removeNeighbor(self, node):
        if node not in self.neighbors:
            return
        del self.neighbors[node]
        del node.neighbors[self]

    def dissolve(self):
        assert self.iscorridor()
        n1, n2 = list(self.neighbors.items())
        # n[0] is the node object, n[1] is the distance
        n1[0].addNeighbor(n2[0], n1[1] + n2[1])
        n1[0].removeNeighbor(self)
        n2[0].removeNeighbor(self)

    def numNeighbors(self):
        return len(self.neighbors)

    def distance(self, other):
        if other in self.neighbors:
            return self.neighbors[other]
        return abs(self.y - other.y) + abs(self.x - other.x)

    def __eq__(self, other):
        return self.y == other.y and self.x == other.x

    def __hash__(self):
        # only hash y and x coordinate
        return hash((self.y, self.x))

    def iscorridor(self):
        return len(self.neighbors) == 2

    def __str__(self):
        neighbors = ", ".join(f"{n.y} {n.x} (dist={n.distance(self)})" for n in self.neighbors)
        return f"Node {self.y} {self.x} ({neighbors})"

    def __repr__(self):
        return self.__str__()


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
        for node in self.nodes.values():
            y = node.y
            x = node.x
            for ny, nx in [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]:
                node.addNeighbor(self.nodes.get((ny, nx), None))

        # zap unneeded nodes
        reduced = True
        zapped = []
        while reduced:
            reduced = False
            for node in self.nodes.values():
                if node.iscorridor():
                    node.dissolve()
                    reduced = True
                    zapped.append((node.y, node.x))
            while zapped:
                node = zapped.pop()
                del self.nodes[node]
        self.nodes = {(node.y, node.x): node for node in self.nodes.values() if node.numNeighbors() > 0}
        return

    def part1(self):
        # we always store distance + 1 so we can abuse this as visited map also
        visited = np.zeros(self.grid.shape, dtype=np.int8)
        start_time = np.zeros(self.grid.shape, dtype=np.uint32)
        end_time = np.zeros(self.grid.shape, dtype=np.uint32)

        def neighbors(y, x):
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

    def calculateLongestDistances(self, part2=False):
        if not part2:
            return self.part1()
        self._buildCompressedGraph()

        from collections import defaultdict
        # we always store distance + 1 so we can abuse this as visited map also
        visited = defaultdict(bool)

        # DFS over queue entries (node, depth, backtrack)
        # we need these backtrack booleans since this is iterative rather than recursive
        stack = [(self.nodes[self.start], 0, False)]
        maxpathlen = 0

        while stack:
            node, d, backtrack = stack.pop()
            if not backtrack and not visited[node]:
                visited[node] = True
                stack.append((node, d, True))  # for backtracking
                # add all edges
                if (node.y, node.x) == self.dest:
                    if d > maxpathlen:
                        logger.debug(f"New max: {d}")
                        maxpathlen = d
                        # write out max distances
                    continue
                for neighbor, distance in node.getNeighbors():
                    if not visited[neighbor]:
                        stack.append((neighbor, d + distance, False))

            elif backtrack:
                # backtrack
                visited[node] = False
        return maxpathlen

    def __str__(self):
        return '\n'.join(''.join(str(x) for x in row) for row in self.grid)


def part1(lines):
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
