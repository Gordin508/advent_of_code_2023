import logging
import sys
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Condition(Enum):
    OPERATIONAL = 0
    BROKEN = 1
    UNKNOWN = 2

    @classmethod
    def from_char(cls, character):
        match character:
            case ".":
                return cls.OPERATIONAL
            case "#":
                return cls.BROKEN
            case "?":
                return cls.UNKNOWN
            case _:
                logger.error(f"Unexpected: {character}")
                exit(1)


class Springs:
    def __init__(self, line: str, isFold=False):
        split = line.strip().split(" ", maxsplit=1)
        self.rawconditions = split[0]
        self.conditions = [Condition.from_char(x) for x in split[0]]
        self.record = [int(x.strip()) for x in split[1].split(",")]
        self.isFold = isFold

    def __str__(self):
        return f"{self.rawconditions} {self.record}"

    def __repr__(self):
        return self.__str__()

    def numPossibilities(self):
        def getUnknowns(conditions):
             return [i for (i, cond) in enumerate(conditions) if cond == Condition.UNKNOWN]

        def liststartswidth(list1, prefix):
            if len(prefix) > len(list1):
                return False
            for x, y in zip(list1, prefix):
                if x != y:
                    return False
            return True

        def checkRecords(conditions, nounknowns=False):
            prefix = []
            current = 0
            for condition in conditions:
                if condition == Condition.UNKNOWN:
                    current = 0
                    break
                elif condition == Condition.OPERATIONAL and current > 0:
                    prefix.append(current)
                    if not liststartswidth(self.record, prefix):
                        return False
                    current = 0
                elif condition == Condition.BROKEN:
                    current += 1
            if current > 0:
                prefix.append(current)
            if nounknowns:
                return prefix == self.record
            else:
                return liststartswidth(self.record, prefix)

        def possibilities(conditions):
            unknown = getUnknowns(conditions)
            conditions = conditions.copy()
            if not checkRecords(conditions, nounknowns=len(unknown) == 0):
                return 0
            if len(unknown) == 0:
                return 1
            conditions[unknown[0]] = Condition.OPERATIONAL
            result = 0
            result += possibilities(conditions)
            conditions[unknown[0]] = Condition.BROKEN
            result += possibilities(conditions)
            return result

        return possibilities(self.conditions)


def part1(lines):
    result = 0
    for line in lines:
        spring = Springs(line)
        possibilities = spring.numPossibilities()
        result += possibilities

    logger.info(f"Part 1: {result}")


def part2(lines):
    import ipdb; ipdb.set_trace()
    result = 0

    for line in lines:
        spring = Springs(line)
        possibilities = spring.numPossibilities()
        spring2 = Springs("?" + line, isFold=True)
        possibilities2 = spring2.numPossibilities()
        tmp = possibilities * (possibilities2**4)
        logger.info(f"{possibilities} {possibilities2}: {tmp}")
        result += tmp

    logger.info(f"Part 2: {result}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    # part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
