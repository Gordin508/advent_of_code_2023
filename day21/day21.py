import logging
import numpy as np
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def reachable(grid, startingposition, steps):
    # how many fields of grid are reachable within steps steps
    queue = [startingposition]
    visited = np.zeros_like(grid)
    visited[0, 0]
    reachable = defaultdict(set)
    reachable[0].add(startingposition)

    def getneighbors(y, x):
        neighbors = []
        for ny, nx in [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]:
            if ny < 0 or ny >= grid.shape[0] or nx < 0 or nx >= grid.shape[1]:
                continue
            if grid[ny, nx] == 0:
                neighbors.append((ny, nx))
        return neighbors

    for step in range(1, steps + 1):
        newq = []
        for y, x in queue:
            for ny, nx in getneighbors(y, x):
                reachable[step].add((ny, nx))
                if visited[ny, nx] == 0:
                    visited[ny, nx] = 1
                    newq.append((ny, nx))
        queue = newq
    resultset = set()
    for i in range(1, steps + 1):
        if i % 2 == 0:
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
