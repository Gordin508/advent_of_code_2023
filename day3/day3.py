import logging
import sys
from enum import Enum


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FieldType(Enum):
    DIGIT = 1
    SYMBOL = 2
    NONE = 3

    @staticmethod
    def get(char: str):
        assert len(char) == 1
        if char.isdigit():
            return FieldType.DIGIT
        elif char == ".":
            return FieldType.NONE
        else:
            return FieldType.SYMBOL


class Grid:
    def __init__(self, lines):
        self.lines = [line.strip() for line in lines]
        self.width = len(self.lines[0])
        self.height = len(self.lines)
        assert all((len(line) == self.width for line in self.lines))

    def get(self, x, y) -> str:
        assert x < self.width, f"x {x}/{self.width} out of range"
        assert y < self.height, f"y {y}/{self.height} out of range"
        return self.lines[y][x]

    def adjascentFields(self, line, startColumn, endColumn):
        # start and endcolumn are inclusive
        for y in range(max(0, line - 1), min(self.height, line + 1 + 1)):
            for x in range(max(0, startColumn - 1), min(self.width, endColumn + 1 + 1)):
                if y != line or x < startColumn or x > endColumn:
                    logger.debug(f"Yield {y}, {x}: {self.get(x, y)}")
                    yield self.get(x, y)

    def getGears(self):
        GEARSYMBOL = "*"
        class GearPart:
            def __init__(self, line, startColumn, endColumn, value):
                self.line = line
                self.startColumn = startColumn
                self.endColumn = endColumn
                self.value = int(value)

            def __str__(self):
                return f"({self.line}, {self.startColumn}): {self.value}"

            def __repr__(self):
                return str(self)

        gearparts = []

        partLookup = [[None]*self.width for _ in range(self.height)]
        import re
        for i, line in enumerate(self.lines):
            for match in re.finditer(r"\d+", line):
                gear = GearPart(line=i, startColumn=match.start(), endColumn=match.end(), value=int(match.string[match.start():match.end()]))
                gearparts.append(gear)
                for x in range(match.start(), match.end()):
                    partLookup[i][x] = gear

        logger.info(f"Found {len(gearparts)} gear parts")
        result = 0
        from functools import reduce
        for i, line in enumerate(self.lines):
            for charpos, c in enumerate(line):
                if c == GEARSYMBOL:
                    # needs to be adjascent to exactly two numbers
                    nums = set()
                    for x, y in self.adjascentFields(i, charpos, charpos):
                        part = partLookup[y][x]
                        if part is not None:
                            nums.add(part)
                    if len(nums) == 2:
                        # gear found
                        logger.debug(f"Found gear at (y, x) {(i, charpos)}")
                        result += reduce(lambda a, b: a*b.value, nums, 1)

        return result




    def adjascentFields(self, line, startColumn, endColumn):
        # start and endcolumn are inclusive
        for y in range(max(0, line - 1), min(self.height, line + 1 + 1)):
            for x in range(max(0, startColumn - 1), min(self.width, endColumn + 1 + 1)):
                if y != line or x < startColumn or x > endColumn:
                    logger.debug(f"Yield {y}, {x}: {self.get(x, y)}")
                    yield (x, y)

    def getEngineParts(self):
        import re

        engineparts = []
        for i, line in enumerate(self.lines):
            for match in re.finditer(r"\d+", line):
                startpos, endpos = match.start(), match.end()
                logger.debug(f"Testing {match}")
                if any((FieldType.get(self.get(x, y)) == FieldType.SYMBOL for x, y in self.adjascentFields(i, startpos, endpos - 1))):
                    engineparts.append(int(match.string[match.start():match.end()]))

        return engineparts


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    with open(infile, 'r') as f:
        lines = f.readlines()
    grid = Grid(lines)
    engineparts = grid.getEngineParts()
    print(f"Part 1 {sum(engineparts)}")
    part2 = grid.getGears()
    print(f"Part 2 {part2}")


if __name__ == "__main__":
    main()
