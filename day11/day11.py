import logging
import sys
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Universe:
    def __init__(self, lines):
        self.width = len(lines[0].strip())
        self.height = len(lines)
        self.grid = np.zeros((self.height, self.width), dtype=np.int8)
        self.galaxymap = {}
        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                match char:
                    case ".":
                        # do nothing
                        pass
                    case "#":
                        self.grid[y][x] = 1
                    case _:
                        logger.error(f"Unexpected at {(y, x)}: {char}")
        self.updateGalaxyMap()
        logger.info(f"Parsed {y} x {x} grid with {self.getNumGalaxies()} galaxies")
        self.age = 1

    def getNumGalaxies(self):
        return len(self.galaxymap)

    def updateGalaxyMap(self):
        self.galaxymap = {}
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                if val == 1:
                    self.galaxymap[len(self.galaxymap)] = (y, x)
        self.reverseGalaxymap = {val: key for (key, val) in self.galaxymap.items()}
        assert np.sum(self.grid) == len(self.galaxymap) == len(self.reverseGalaxymap)

    def setVirtualAge(self, age):
        self.age = age
        self.emptyrows = [y for y in range(self.height) if np.sum(self.grid[y]) == 0]
        self.emptycolumns = [x for x in range(self.width) if np.sum(self.grid[:,x]) == 0]

    def getDistance(self, galaxy1: int, galaxy2: int):
        g1pos = self.galaxymap[galaxy1]
        g2pos = self.galaxymap[galaxy2]
        rawdist = abs(g1pos[0] - g2pos[0]) + abs(g1pos[1] - g2pos[1])

        def minmax(pos1, pos2, axis):
            return (min(pos1[axis], pos2[axis]), max(pos1[axis], pos2[axis]))
        # how many expanding rows and columns are we crossing?
        y1, y2 = minmax(g1pos, g2pos, 0)
        x1, x2 = minmax(g1pos, g2pos, 1)
        emptyrows = len([row for row in self.emptyrows if row > y1 and row < y2])
        emptycolumns = len([col for col in self.emptycolumns if col > x1 and col < x2])
        return rawdist + (emptycolumns + emptyrows) * self.age

    def expand(self):
        # use only for part1!
        emptyrows = [y for y in range(self.height) if np.sum(self.grid[y]) == 0]
        emptycolumns = [x for x in range(self.width) if np.sum(self.grid[:,x]) == 0]
        if len(emptyrows) != 0:
            # first insert new rows
            last = 0
            newrows = []
            for y in emptyrows:
                newrow = np.zeros(self.width, dtype=self.grid.dtype).reshape(1, -1)
                newrows.append(self.grid[last:y + 1])
                newrows.append(newrow)
                last = y + 1
            newrows.append(self.grid[last:])

            self.grid = np.concatenate(newrows, axis=0)
            self.height = self.grid.shape[0]

        # then insert new columns
        if len(emptyrows) != 0:
            # first insert new rows
            last = 0
            newcols = []
            for y in emptycolumns:
                newcol = np.zeros(self.height, dtype=self.grid.dtype).reshape(-1, 1)
                newcols.append(self.grid[:,last:y + 1])
                newcols.append(newcol)
                last = y + 1
            newcols.append(self.grid[:,last:])

            self.grid = np.concatenate(newcols, axis=1)
            self.width = self.grid.shape[1]

        self.updateGalaxyMap()

    def __str__(self):
        out = ""
        for row in self.grid:
            for val in row:
                match(val):
                    case 0:
                        out += "."
                    case 1:
                        out += "#"
                    case _:
                        logger.error(f"Unexpected int: {val}")
            out += '\n'
        return out

    def __repr__(self):
        return self.__str__()

    def shortestPaths(self, usevirtual=False):
        # pairwise shortest paths
        pathlengths = []
        numgalaxies = self.getNumGalaxies()
        if not usevirtual:
            for g1, g2 in ((g1, g2) for g1 in range(0, numgalaxies) for g2 in range(g1 + 1, numgalaxies)):
                g1pos = self.galaxymap[g1]
                g2pos = self.galaxymap[g2]
                pathlengths.append(abs(g1pos[0] - g2pos[0]) + abs(g1pos[1] - g2pos[1]))
                logger.debug(f"{(g1, g2)}: distance {pathlengths[-1]}")
        else:
            for g1, g2 in ((g1, g2) for g1 in range(0, numgalaxies) for g2 in range(g1 + 1, numgalaxies)):
                pathlengths.append(self.getDistance(g1, g2))

        return sum(pathlengths)


def part1(lines):
    universe = Universe(lines)
    universe.setVirtualAge(1)
    # print(universe)
    print(f"Part 1: {universe.shortestPaths(usevirtual=True)}")


def part2(lines):
    universe = Universe(lines)
    universe.setVirtualAge(int(1e6) - 1)
    # print(universe)
    print(f"Part 2: {universe.shortestPaths(usevirtual=True)}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
