import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Node:
    def __init__(self, letter, y, x):
        self.neighbors = set()
        assert len(letter) == 1
        assert letter in "|-JF7SL."
        self.letter = letter
        self.x = x
        self.y = y
        self.facing = (0, 0) # loop orientation

    def isDirt(self):
        return self.letter == "."

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

    def walk(self):
        # return iterator over all tiles in the loop
        assert len(self.neighbors) == 2
        neighbors = list(self.neighbors)
        current, last = neighbors[0], self
        loop = [last]
        while (current != self):
            loop.append(current)
            yield current
            current, last = [n for n in current.getNeighbors() if n != last][0], current
        for i, node in enumerate(loop):
            n, p = (i + 1) % len(loop), (i - 1 + len(loop)) % len(loop)
            node.facing = (loop[n].y - loop[p].y, loop[n].x - loop[p].x)
        return

    def facingDirection(self):
        if self.facing == (0, 0):
            return None
        out = ""
        assert abs(self.facing[1]) + abs(self.facing[0]) == 2, f"{self.facing} {self}"
        if self.facing[0] != 0:
            out += "U" if self.facing[0] < 0 else "D"
        out += "L" if self.facing[1] < 0 else "R"
        return out

    def isloopnode(self):
        if self.facingDirection() is not None:
            assert self.letter != "."
            return True
        return False

    def isjunk(self):
        return not self.isloopnode()

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
        return self.grid[y][x] if self.grid[y][x] is not None else Node(".", y, x)

    def __str__(self):
        return f"Pipesystem with {len(self.nodes)} nodes, starting it {self.start}"

    def __repr__(self):
        return self.__str__()

    def getNestSize(self):
        bb = self.getLoopBoundingBox()
        bb = (0, 0, self.height - 1, self.width - 1)
        logger.info(f"Calculated BB:")
        visited = [[0 for _ in range(bb[3] - bb[1] + 1)] for _ in range(bb[2] - bb[0] + 1)]

        nestsize = 0
        ccw = True
        for x in range(self.start.x + 1):
            node = self.getGridNode(self.start.y, x)
            if node.isloopnode():
                ccw = True if "D" in node.facingDirection() else False
                break

        def setvisited(y, x, val=1):
            if y < 0 or y >= len(visited):
                return
            if x < 0 or x >= len(visited[0]):
                return
            visited[y + bb[0]][x + bb[1]] = val

        def getvisited(y, x):
            if y < 0 or y >= len(visited):
                return 0
            if x < 0 or x >= len(visited[0]):
                return 0
            return visited[y + bb[0]][x + bb[1]]

        def flood(y, x):
            if visited[y][x]:
                return 0
            borderingLoopnode = None
            total = 1
            firstnode = self.getGridNode(y, x)
            queue = [firstnode]
            allseen = [firstnode]
            if not firstnode.isjunk():
                return 0
            logger.debug(f"Flooding at node {(y, x)}")
            setvisited(y, x)
            while (len(queue) > 0):
                for node in queue:
                    y, x = node.y, node.x
                    adjascent = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
                    adjascent = [self.getGridNode(y, x) for (y, x) in adjascent]
                    adjascent = list(filter(lambda x: x is not None, adjascent))
                    loopnodes = [node for node in adjascent if node.isloopnode()]
                    if borderingLoopnode is None and len(loopnodes) > 0:
                        # now we can check which side of the loop we are on
                        borderingLoopnode = (node, loopnodes[0])
                    adjascent = list(filter(lambda node: not getvisited(node.y, node.x), adjascent))
                    total += sum((1 for node in adjascent if node.isjunk()))
                    queue = list(filter(lambda node: node.isjunk(), adjascent))
                    for node in queue:
                        setvisited(node.y, node.x)
                    assert all((node.isjunk() for node in queue))
                    allseen.extend(queue)

            # now that we collected the total of dirt nodes, check whether we are in or out
            if borderingLoopnode is None:
                walkx = firstnode.x - 1
                while (walkx >= 0):
                    node = self.getGridNode(firstnode.y, walkx)
                    if node.isloopnode():
                        borderingLoopnode = (firstnode, node)
                        break
                    walkx -= 1

            if borderingLoopnode is None:
                # definitely outside
                return 0

            innernode, bordernode = borderingLoopnode
            if innernode.x < bordernode.x:
                isInside = "U" in bordernode.facingDirection()
            elif innernode.y < bordernode.y:
                isInside = "R" in bordernode.facingDirection()
            elif innernode.x > bordernode.x:
                isInside = "D" in bordernode.facingDirection()
            elif innernode.y > bordernode.y:
                isInside = "L" in bordernode.facingDirection()

            if not ccw:
                isInside = not isInside
            if not isInside:
                return 0
            else:
                for node in allseen:
                    setvisited(node.y, node.x, val=2)
                return total

        for y, line in enumerate(self.grid):
            for x, node in enumerate(line):
                node = self.getGridNode(y, x) if node is None else node
                if node.isjunk() and not getvisited(y, x):
                    nestsize += flood(y, x)

        def drawGrid():
            for y, line in enumerate(self.grid):
                for x, node in enumerate(line):
                    if node is None:
                        node = self.getGridNode(y, x)
                    if not node.isjunk():
                        print(node.letter, end="")
                    else:
                        match getvisited(y, x):
                            case 0:
                                print(".", end="")
                            case 1:
                                print("O", end="")
                            case 2:
                                print("I", end="")
                            case _:
                                print(getvisited(y, x), end="")
                print("")
        drawGrid()
        logger.info(f"Counter clock-wise: {ccw}")
        return nestsize


    def getLoopBoundingBox(self):
        # y1, x1, y2, x2
        y1 = self.start.y
        x1 = self.start.x
        y2 = y1
        x2 = x1

        for node in self.start.walk():
            y1 = min(node.y, y1)
            y2 = max(node.y, y2)
            x1 = min(node.x, x1)
            x2 = min(node.y, x2)

        return (y1, x2, y2, x2)


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
    return pipes


def part2(lines):
    pipes = part1(lines)
    nestsize = pipes.getNestSize()
    logger.info(f"Part 2: {nestsize}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    # part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
