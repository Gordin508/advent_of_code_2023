import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Race:
    def __init__(self, time, distance):
        self.time = int(time)
        self.distance = int(distance)

    def __str__(self):
        return f'{self.time}ms {self.distance}mm'

    def __repr__(self):
        return self.__str__()

    def numWinPossibilities(self):
        p = 0
        for speed in range(1, self.time):
            if self.distance < speed * (self.time - speed):
                p += 1
        return p

    def winning(self, holdtime):
        return (holdtime**2 - holdtime*self.time + self.distance < 0)

    def numWinPossibilitiesImproved(self):
        # so we win if
        # speed * self.time - speed * speed - self.distance
        # is greater than zero -> find zero-point of this function

        # 1 * X**2 - X * self.time + self.distance
        import math
        ph = self.time / 2
        braket = math.sqrt(ph**2 - self.distance)
        x1 = math.ceil(max(1, ph - braket))
        x2 = math.floor(max(1, ph + braket))
        if not self.winning(x1):
            x1 += 1
        if not self.winning(x2):
            x2 -= 1
        return max(0, x2 - x1 + 1)


def parseinput(lines):
    times = [int(val) for val in re.findall(r'\d+', lines[0])]
    distances = [int(val) for val in re.findall(r'\d+', lines[1])]
    races = [Race(time, distance) for (time, distance) in zip(times, distances)]
    return races


def parseinput2(lines):
    time = int(next(re.finditer(r'[\d\s]+', lines[0])).group(0).strip().replace(" ", ""))
    distance = int(next(re.finditer(r'[\d\s]+', lines[1])).group(0).strip().replace(" ", ""))
    race = Race(time, distance)
    return race


def part1(lines):
    races = parseinput(lines)
    result = 1
    for r in races:
        result *= r.numWinPossibilitiesImproved()
    logger.info(f"Part 1: {result}")


def part2(lines):
    race = parseinput2(lines)
    result = race.numWinPossibilitiesImproved()
    logger.info(f"Part 2: {result}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
