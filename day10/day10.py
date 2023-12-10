import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Node:
    def __init__(self, letter, y, x):
        self.neighbors = set()
        assert len(letter) == 1
        assert letter in "|-JF7SL"
        self.letter = letter
        self.x = x
        self.y = y

    def addNeighbor(self, neighbor, norecurse=False):
        if neighbor is None:
            return
        if not self.connects(neighbor):
            return
        self.neighbors.add(neighbor)
        if not norecurse:
            neighbor.addNeighbor(self, norecurse=True)
        assert (len(self.neighbors)) <= 2

    def getNeighbors(self):
        return self.neighbors

    def __str__(self):
        othercoords = [(other.y, other.x) for other in self.neighbors]
        return f"{self.letter} ({self.y}, {self.x}): connected to {len(self.neighbors)} nodes ({othercoords})"

    def __repr__(self):
        return self.__str__()

    def above(self, other):
        return other.y == self.y + 1

    def below(self, other):
        return other.y == self.y - 1

    def leftof(self, other):
        return other.x == self.x + 1

    def rightof(self, other):
        return other.x == self.x - 1

    def beside(self, other):
        return self.rightof(other) or self.leftof(other)

    def stacked(self, other):
        return self.below(other) or self.above(other)

    def connectors(self):
        connectors = []
        if self.letter == "S":
            return "NESW"
        if self.letter in "|LJ":
            connectors.append("N")
        if self.letter in "-J7":
            connectors.append("W")
        if self.letter in "-FL":
            connectors.append("E")
        if self.letter in "F7|":
            connectors.append("S")
        return "".join(connectors)

    def connects(self, other):
        top = self if (self.leftof(other) or self.above(other)) else other
        bottom = self if top is not self else other
        if self.letter == "L":
            pass
        topc = top.connectors()
        bottomc = bottom.connectors()
        if top.above(bottom):
            return "S" in topc and "N" in bottomc
        if top.leftof(bottom):
            return "E" in topc and "W" in bottomc
        return False


class PipeSystem:
    def __init__(self, lines):
        lines = [line.strip() for line in lines]
        self.width = len(lines[0])
        self.height = len(lines)
        for line in lines:
            assert (len(line)) == self.width
        # nodes is an y*x array
        grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        startnode = None

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                match char:
                    case ".":
                        continue
                    case "S":
                        startnode = Node(char, y, x)
                        grid[y][x] = startnode
                    case _:
                        grid[y][x] = Node(char, y, x)
        self.grid = grid
        for y, line in enumerate(self.grid):
            for x, node in enumerate(line):
                if node is None:
                    continue
                neighbors = []
                match node.letter:
                    case "|":
                        neighbors.append((y - 1, x))
                        neighbors.append((y + 1, x))
                    case "-":
                        neighbors.append((y, x + 1))
                        neighbors.append((y, x - 1))
                    case "L":
                        neighbors.append((y - 1, x))
                        neighbors.append((y, x + 1))
                    case "J":
                        neighbors.append((y - 1, x))
                        neighbors.append((y, x - 1))
                    case "7":
                        neighbors.append((y + 1, x))
                        neighbors.append((y, x - 1))
                    case "F":
                        neighbors.append((y + 1, x))
                        neighbors.append((y, x + 1))
                    case "S":
                        assert node == startnode
                        neighbors = [(y, x - 1), (y, x + 1), (y - 1, x), (y + 1, x)]
                    case _:
                        logger.error(f"Invalid letter: {node.letter}")

                for j, i in neighbors:
                    node.addNeighbor(self.getGridNode(j, i))
        self.nodes = set((node for line in grid for node in line if node is not None))
        for node in self.nodes:
            assert len(node.getNeighbors()) <= 2, f"Node {node} has too many neighbors: {node.getNeighbors()}"
        self.start = startnode
        logger.info(f"Created {len(self.nodes)} nodes.")

    def getGridNode(self, y, x):
        if y < 0 or y >= self.height:
            return None
        if x < 0 or x >= self.width:
            return None
        return self.grid[y][x]

    def __str__(self):
        return f"Pipesystem with {len(self.nodes)} nodes, starting it {self.start}"

    def __repr__(self):
        return self.__str__()

    def getFarthestNode(self):
        if self.start is None:
            self.start = next((node for node in self.nodes if node.letter == "S"))
        assert self.start is not None

        # BFS
        distmap = {node: -1 for node in self.nodes}
        currentdist = 0
        queue = [self.start]

        def visited(node):
            return distmap[node] > -1
        while (len(queue) > 0):
            for node in queue:
                distmap[node] = currentdist
            currentdist += 1
            queue = [neighbor for node in queue for neighbor in node.getNeighbors() if not visited(neighbor)]
        return currentdist - 1


def part1(lines):
    pipes = PipeSystem(lines)
    logger.info(f"Part 1: {pipes.getFarthestNode()}")


def part2(lines):
    import ipdb; ipdb.set_trace()
    pass


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
