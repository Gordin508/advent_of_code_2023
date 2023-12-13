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


def findReflections(grid: np.ndarray, smudge):
    assert len(grid.shape) == 2, f"Unexpected shape: {grid.shape}"

    def testhreflect(startval, smudge):
        height = min(startval + 1, grid.shape[0] - startval - 1)
        differences = np.sum(grid[startval - height + 1: startval + 1][::-1]
                             != grid[startval + 1: startval + 1 + height])
        return differences == 0 if not smudge else differences == 1

    def testvreflect(startval, smudge):
        width = min(startval + 1, grid.shape[1] - startval - 1)
        differences = np.sum(grid[:, startval - width + 1:startval + 1][:, ::-1]
                             != grid[:, startval + 1:startval + 1 + width])
        return differences == 0 if not smudge else differences == 1

    horizontal = [y + 1 for y in range(grid.shape[0] - 1) if testhreflect(y, smudge)]
    vertical = [x + 1 for x in range(grid.shape[1] - 1) if testvreflect(x, smudge)]
    return (horizontal, vertical)


def reflectionScore(lines, smudge=False):
    grid = parsegrid(lines)
    assert len(grid.shape) == 2
    horizontal, vertical = findReflections(grid, smudge)
    assert len(horizontal) + len(vertical) == 1
    hval = horizontal[0] if horizontal else 0
    vval = vertical[0] if vertical else 0
    return hval * 100 + vval


def worlditer(lines):
    currentworld = []
    for i, line in enumerate(lines):
        if len(line.strip()) > 0:
            currentworld.append(line)
        else:
            yield currentworld
            currentworld = []
    if currentworld:
        yield currentworld


def part1(lines):
    return sum((reflectionScore(world) for world in worlditer(lines)))


def part2(lines):
    return sum((reflectionScore(world, smudge=True) for world in worlditer(lines)))


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    for i, fun in enumerate((part1, part2), start=1):
        result = fun(lines)
        if result is None:
            logger.debug(f"Part {i} not yet implemented")
            continue
        logger.info(f"Part {i}: {result}")


if __name__ == '__main__':
    main()
