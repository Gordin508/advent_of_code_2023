import logging
import sys
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parsegrid(lines):
    lines = [line.strip() for line in lines if len(line.strip()) > 0]
    if not lines:
        return 0
    return np.array([[x == "#" for x in line] for line in lines], np.int8)

def findHorizontalReflections(grid: np.ndarray):
    horizontalreflections = []
    assert len(grid.shape) == 2, f"Unexpected shape: {grid.shape}"

    def testreflect(startval):
        for i in range(min(startval + 1, grid.shape[0] - startval - 1)):
            if np.any(grid[startval - i] != grid[startval + i + 1]):
                return False
        return True

    for y in range(grid.shape[0] - 1):
        if testreflect(y):
            horizontalreflections.append(y + 1)
    return horizontalreflections


def findVerticalReflections(grid: np.ndarray):
    assert len(grid.shape) == 2, f"Unexpected shape: {grid.shape}"
    reflections = []

    def testreflect(startval):
        for i in range(min(startval + 1, grid.shape[1] - startval - 1)):
            if np.any(grid[:, startval - i] != grid[:, startval + i + 1]):
                return False
        return True

    for x in range(grid.shape[1] - 1):
        if testreflect(x):
            reflections.append(x + 1)
    return reflections


def findPatternReflection(lines):
    grid = parsegrid(lines)
    horizontal = findHorizontalReflections(grid)
    vertical = findVerticalReflections(grid)
    xval = horizontal[0] if horizontal else 0
    yval = vertical[0] if vertical else 0
    return xval * 100 + yval


def part1(lines):
    # we need to find empty lines
    currentworld = []
    result = 0
    for i, line in enumerate(lines):
        if len(line.strip()) > 0:
            currentworld.append(line)
        else:
            result += findPatternReflection(currentworld)
            currentworld = []
    result += findPatternReflection(currentworld)
    return result


def part2(lines):
    pass


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    for i, fun in enumerate((part1, part2), start=1):
        result = fun(lines)
        if result is None:
            logger.debug(f"Part {i} not yet implemented")
            continue
        logger.info(f"Part 1: {result}")


if __name__ == '__main__':
    main()
