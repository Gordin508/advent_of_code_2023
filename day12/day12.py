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
        if isFold:
            self.rawconditions = "?".join(self.rawconditions for _ in range(5))
        self.conditions = [Condition.from_char(x) for x in self.rawconditions]
        self.record = [int(x.strip()) for x in split[1].split(",")]
        if isFold:
            self.record = [x for _ in range(5) for x in self.record]

    def __str__(self):
        return f"{self.rawconditions} {self.record}"

    def __repr__(self):
        return self.__str__()

    def possibilities(self):
        # dynamic programming
        from functools import cache

        @cache
        def possfunc(numindices, numrecords):
            assert len(self.record) >= numrecords >= 0
            assert len(self.conditions) >= numindices >= 0

            if numindices == 0 and numrecords == 0:
                # base case
                return 1

            if numrecords == 0:
                # no more spring may be broken
                return 1 if all(condition != Condition.BROKEN for condition in self.conditions[:numindices]) else 0

            currentstreak = self.record[numrecords - 1]

            if currentstreak > numindices:
                # demanded number is higher than number of springs left
                return 0

            if self.conditions[numindices - 1] == Condition.OPERATIONAL:
                # fast forward, we do not care for operational wells
                return possfunc(numindices - 1, numrecords)

            result = 0
            if all(condition != Condition.OPERATIONAL for condition
                   in (self.conditions[i] for i in range(numindices - currentstreak, numindices))):
                if currentstreak == numindices or self.conditions[numindices - currentstreak - 1] != Condition.BROKEN:
                    # streak is not too short and not too long, so we can pop of the last record
                    result += possfunc(max(0, numindices - currentstreak - 1), numrecords - 1)
            if self.conditions[numindices - 1] == Condition.UNKNOWN:
                # we have a question mark at the current pos
                # we also consider the possibilties where we set it to operational
                result += possfunc(numindices - 1, numrecords)
            return result

        return possfunc(len(self.conditions), len(self.record))

    def possibilities_bruteforce(self):
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
        result += spring.possibilities()

    logger.info(f"Part 1: {result}")


def part2(lines):
    result = 0

    import ipdb; ipdb.set_trace()
    for line in lines:
        spring = Springs(line, isFold=True)
        result += spring.possibilities()

    logger.info(f"Part 2: {result}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
