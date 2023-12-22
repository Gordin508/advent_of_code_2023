import logging
from enum import Enum
import re
from collections import defaultdict

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Orientation(Enum):
    VERTICAL = 1
    HORIZONTALX = 2
    HORIZONTALY = 3
    OTHER = 4

    def __str__(self):
        return self.name


class Size:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.orientation = self._getorientation()

    def __str__(self):
        return f"{self.orientation}: ({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return self.__str__()

    def _getorientation(self):
        if self.x == self.y == 1:
            return Orientation.VERTICAL
        if self.x > 1 and (self.y == 1 and self.z == 1):
            return Orientation.HORIZONTALX
        if self.y > 1 and (self.x == 1 and self.z == 1):
            return Orientation.HORIZONTALY
        return Orientation.OTHER


class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return self.__str__()

    def __sub__(self, other):
        if not isinstance(other, type(self)):
            raise NotImplementedError()
        return Size(abs(self.x - other.x) + 1, abs(self.y - other.y) + 1, abs(self.z - other.z) + 1)

    def __lt__(self, other):
        assert isinstance(other, type(self))
        return self.z < other.z

    def __gt__(self, other):
        return self.z > other.z

    def __eq__(self, other):
        return self.z == other.z and self.y == other.y and self.x == other.x


class Brick:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end
        if (self.end < self.start):
            # start is never above end
            self.start, self.end = self.end, self.start
        self.size = start - end

    def __lt__(self, other):
        assert isinstance(other, type(self))
        return self.start < other.start

    def __gt__(self, other):
        assert isinstance(other, type(self))
        return self.start > other.start

    def __str__(self):
        return f"{self.start} {self.end} (dimensions: {self.size})"

    def __repr__(self):
        return self.__str__()

    def _toxrange(self):
        return (min(self.start.x, self.end.x), max(self.start.x, self.end.x))

    def _toyrange(self):
        return (min(self.start.y, self.end.y), max(self.start.y, self.end.y))

    def moveZ(self, newz):
        assert newz > 0
        self.start.z = newz
        self.end.z = newz + self.size.z - 1

    @staticmethod
    def _rangeintersect(r1, r2):
        if r1 > r2:
            r1, r2 = r2, r1
        if r1[1] < r2[0] or r1[0] > r2[1]:
            return False
        return True

    def intersect(self, other):
        # test if two bricks intersect on xy axis
        assert isinstance(other, type(self))

        return Brick._rangeintersect(self._toxrange(), other._toxrange()) \
            and Brick._rangeintersect(self._toyrange(), other._toyrange())

    @classmethod
    def from_line(cls, line: str):
        regex = re.compile(r"\d+")
        numbers = [int(x) for x in regex.findall(line)]
        assert len(numbers) == 6
        start = Position(*numbers[:3])
        end = Position(*numbers[3:])
        return Brick(start, end)


def parsebricks_and_settle(lines):
    bricks = list(sorted((Brick.from_line(line) for line in lines), reverse=False))
    logger.info(f"Parsed {len(bricks)} bricks")

    settled = defaultdict(list)
    supports = defaultdict(list)
    supportedby = defaultdict(list)

    for lowest in bricks:
        searchz = lowest.start.z - 1
        while searchz > 0:
            supportfound = False
            for brick in settled[searchz]:
                if brick.intersect(lowest):
                    supports[brick].append(lowest)
                    supportedby[lowest].append(brick)
                    supportfound = True
            if supportfound:
                break
            searchz -= 1
        lowest.moveZ(searchz + 1)
        settled[lowest.end.z].append(lowest)
    return bricks, settled, supports, supportedby


def collapse(bricks, settled, supports, supportedby, desintegratedbrick) -> int:
    # how many bricks fall if brick is desintegrated
    # supports and supportedby imply a directed graph

    # check graph integrity for safety
    for brick, supportedlist in supports.items():
        for sbrick in supportedlist:
            assert brick in supportedby[sbrick], f"{brick} supports {sbrick}, but is not in supportedby."

    if not supports[desintegratedbrick]:
        # the removed brick does not support anything
        return 0
    elif all(len(supportedby[sbrick]) > 1 for sbrick in supports[desintegratedbrick]):
        # ever sbrick supported by brick is also supported by at least one other brick
        return 0

    def collapse(brick):
        # remove brick from the graph
        affected = set()
        for supportedbrick in supports[brick]:
            supportedby[supportedbrick].remove(brick)
            affected.add(supportedbrick)
        del supports[brick]
        if brick in supportedby:
            del supportedby[brick]
        return affected

    affected = collapse(desintegratedbrick)
    result = 0

    while affected:
        # while at least one brick has been removed in the previous step,
        # check if other bricks are removed as a result
        falling = []
        newaffected = set()
        for brick in affected:
            supportbricks = supportedby[brick]
            if brick.start.z > 1 and len(supportbricks) == 0:
                # brick is neither supported by ground nor by any remaining brick
                # we remember this brick for now, as we can not manipulate supportedby
                # while iterating over it
                falling.append(brick)

        for brick in falling:
            # remove all unsupported bricks from the graph
            newaffected.update(collapse(brick))
        result += len(falling)
        affected = newaffected

    return result


part2result = None


def part1(lines):
    global part2result
    bricks, settled, osupports, osupportedby = parsebricks_and_settle(lines)

    result = 0
    part2result = 0
    for brick in bricks:
        # we copy the support lists as we need to manipulate inside the collapse function
        supports = defaultdict(list)
        for key, value in osupports.items():
            supports[key] = value.copy()
        supportedby = defaultdict(list)
        for key, value in osupportedby.items():
            supportedby[key] = value.copy()
        falling = collapse(bricks, settled, supports, supportedby, brick)

        # falling is the number of bricks which have fallen as a result
        # of removing the brick
        if falling == 0:
            # this means we can safely desintegrate this brick
            result += 1
        else:
            # the number of falling bricks is relevant to part2
            part2result += falling
    return result


def part2(lines):
    global part2result
    if part2result is not None:
        # calculated by part1 already
        return part2result

    bricks, settled, osupports, osupportedby = parsebricks_and_settle(lines)

    result = 0
    for brick in bricks:
        # we copy the support lists as we need to manipulate them now
        supports = defaultdict(list)
        for key, value in osupports.items():
            supports[key] = value.copy()
        supportedby = defaultdict(list)
        for key, value in osupportedby.items():
            supportedby[key] = value.copy()
        result += collapse(bricks, settled, supports, supportedby, brick)
    return result


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
