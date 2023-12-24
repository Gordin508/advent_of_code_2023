import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


hailstone_identifier = 0


def sign(x):
    return -1 if x < 0 else 1


class HailStone:
    def __init__(self, x, y, z, vx, vy, vz):
        global hailstone_identifier
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.identifier = hailstone_identifier
        hailstone_identifier += 1

        a = -self.x / self.vx
        self.b = self.y + a * self.vy
        self.a = self.vy / self.vx
        # equation is self.y = self.a * x + self.b

    @classmethod
    def from_line(cls, line):
        numbers = line.replace(" @", ",").split(",")
        assert len(numbers) == 6
        return cls(*(int(num.strip()) for num in numbers))

    def __str__(self):
        return f"HS {self.identifier}: {self.x} {self.y} {self.z} (Velocity: {self.vx} {self.vy} {self.vz})"

    def __repr__(self):
        return self.__str__()

    def intersectXY(self, other):
        # give the position where the paths of self and other intersect
        # self.a * x + self.b == other.a * x + other.b
        # (self.a - other.a) * x == other.b - self.b
        # x == (other.b - self.b) / (self.a - other.a)
        divisor = self.a - other.a
        if abs(divisor) < 1e-6:
            return None
        x = (other.b - self.b) / divisor
        y = self.a * x + self.b
        # we also need to check whether intersection has been in the past
        if sign(x - self.x) != sign(self.vx) or sign(x - other.x) != sign(other.vx):
            return None
        return (x, y)

    def __eq__(self, other):
        return self.identifier == other.identifier


def part1(lines):
    stones = [HailStone.from_line(line) for line in lines]
    result = 0

    def insideTestArea(x, y):
        #  Look for intersections that happen with an X and Y position each
        # at least 200000000000000 and at most 400000000000000.
        # Disregard the Z axis entirely.
        LOWERBOUND = 200000000000000
        UPPERBOUND = 400000000000000
        # LOWERBOUND = 7  # test values
        # UPPERBOUND = 27
        for coord in (x, y):
            if coord < LOWERBOUND or coord > UPPERBOUND:
                return False
        return True

    for i, stone1 in enumerate(stones):
        for stone2 in ((stones[j] for j in range(i + 1, len(stones)))):
            assert stone1 != stone2
            intersection = stone1.intersectXY(stone2)
            if intersection is None:
                continue
            if insideTestArea(*intersection):
                # logger.debug(f"{stone1} and {stone2} intersect at {intersection}")
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
