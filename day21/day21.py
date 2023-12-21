import logging
import numpy as np
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def reachable(grid, startingposition, steps, repeat_wrap=0):
    # how many fields of grid are reachable within steps steps
    height = grid.shape[0]
    width = grid.shape[1]

    queue = [startingposition]
    visited = np.zeros((grid.shape[0] * (1 + repeat_wrap * 2), grid.shape[1] * (1 + repeat_wrap * 2)))
    reachable = defaultdict(set)
    reachable[0].add(startingposition)

    def visitedIndex(y, x):
        return (y + repeat_wrap * height, x + repeat_wrap * width)

    vy, vx = visitedIndex(*startingposition)
    visited[vy, vx] = 1

    def getneighbors(y, x):
        neighbors = []
        for ny, nx in [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]:
            if ny < 0 - repeat_wrap * height or ny >= grid.shape[0] + repeat_wrap * height \
                    or nx < 0 - repeat_wrap * width or nx >= grid.shape[1] + repeat_wrap * width:
                logger.error(f"Walked off the grid {(ny, nx)}")
                exit(1)
                continue
            if grid[(ny + grid.shape[0]) % grid.shape[0], (nx + grid.shape[1]) % grid.shape[1]] == 0:
                neighbors.append((ny, nx))
        return neighbors

    for step in range(1, steps + 1):
        newq = []
        for y, x in queue:
            for ny, nx in getneighbors(y, x):
                reachable[step].add((ny, nx))
                vy, vx = visitedIndex(ny, nx)
                if visited[vy, vx] == 0:
                    visited[vy, vx] = 1
                    newq.append((ny, nx))
        queue = newq
    resultset = set()
    searchmod = steps % 2
    for i in range(1, min(steps + 1, len(visited) + 1)):
        if i % 2 == searchmod:
            resultset.update(reachable[i])
    return len(resultset)


def part1(lines):
    startingpos = None
    grid = np.zeros((len(lines), len(lines[0].strip())), dtype=np.int8)
    for y, line in enumerate(lines):
        for x, tile in enumerate(line.strip()):
            grid[y, x] = 1 if tile == "#" else 0
            if tile == "S":
                startingpos = (y, x)
    assert startingpos is not None
    return reachable(grid, startingpos, 64)


def part2(lines):
    startingpos = None
    grid = np.zeros((len(lines), len(lines[0].strip())), dtype=np.int8)
    height, width = grid.shape
    assert height == width
    for y, line in enumerate(lines):
        for x, tile in enumerate(line.strip()):
            grid[y, x] = 1 if tile == "#" else 0
            if tile == "S":
                startingpos = (y, x)
    assert startingpos is not None
    STEPS = 26501365
    n = STEPS // height
    remainder = STEPS % height
    supports = np.array([reachable(grid, startingpos, steps=remainder + x * height, repeat_wrap=x) for x in range(3)])

    # solve quadratic equation
    # a * x**2 + b * x + c = y
    # we have supports for x in [0, 1, 2]
    x = np.linalg.solve(np.vander(list(range(3))), supports).astype(np.int64)

    a, b, c = x
    return a * n**2 + b * n + c


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
