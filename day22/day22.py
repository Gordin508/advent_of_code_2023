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


def part1(lines):
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

    #for zvalue, settledbricks in settled.items():
    #    logger.debug(zvalue)
    #    logger.debug("\n".join((str(brick) for brick in settledbricks)))
    import ipdb; ipdb.set_trace()

    result = 0
    for brick in bricks:
        if not supports[brick]:
            result += 1
        elif all(len(supportedby[sbrick]) > 1 for sbrick in supports[brick]):
            # ever sbrick supported by brick is also supported by another brick
            result += 1
    return result


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
