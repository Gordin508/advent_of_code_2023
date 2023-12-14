import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def tiltUpDown(grid, direction):
    assert direction in ["north", "south"]
    direction = 1 if direction == "north" else -1
    height = len(grid)
    for y, line in enumerate(grid[::direction]):
        if direction == -1:
            y = height - 1 - y
        for x, tile in enumerate(line):
            # if there is a rounded rock, move it north till it hits an obstacle
            match tile:
                case "O":
                    destination = y
                    while (destination > 0 if direction > 0 else destination < height - 1) and grid[destination - direction][x] == ".":
                        destination -= direction
                    grid[y][x] = "."
                    grid[destination][x] = "O"  # can equal y
                case _:
                    continue


def tiltLeftRight(grid, direction):
    assert direction in ["east", "west"]
    direction = 1 if direction == "west" else -1
    width = len(grid[0])
    height = len(grid)
    for x in range(width):
        if direction == -1:
            x = width - 1 - x
        for y in range(height):
            tile = grid[y][x]
            match tile:
                case "O":
                    destination = x
                    while (destination > 0 if direction > 0 else destination < width - 1) and grid[y][destination - direction] == ".":
                        destination -= direction
                    grid[y][x] = "."
                    grid[y][destination] = "O"
                case _:
                    continue


def tiltnorth(grid):
    tiltUpDown(grid, direction="north")


def tiltsouth(grid):
    tiltUpDown(grid, direction="south")


def tilteast(grid):
    tiltLeftRight(grid, direction="east")


def tiltwest(grid):
    tiltLeftRight(grid, direction="west")


def printgrid(grid):
    for line in grid:
        print("".join(line))
    print("")


def calculateLoad(grid):
    total = 0
    import numpy as np
    if not isinstance(grid, np.ndarray):
        for y, line in enumerate(grid):
            loadfactor = len(grid) - y
            total += loadfactor * len([tile for tile in line if tile == "O"])
    else:
        if len(grid.shape) == 2:
            grid = np.sum(grid, axis=1, dtype=np.uint64)
        total = np.sum(np.arange(grid.shape[0], 0, -1, dtype=np.uint64) * grid, dtype=np.uint64)
    return total


def spinCycle(grid, printout=False):
    # north west south east
    tiltnorth(grid)
    tiltwest(grid)
    tiltsouth(grid)
    tilteast(grid)
    if printout:
        printgrid(grid)
    return grid


def part1(lines):
    grid = [list(line.strip()) for line in lines]
    assert min((len(line) for line in grid)) == max((len(line) for line in grid))

    tiltnorth(grid)

    return calculateLoad(grid)


def part2(lines):
    grid = [list(line.strip()) for line in lines]
    assert min((len(line) for line in grid)) == max((len(line) for line in grid))
    # import ipdb; ipdb.set_trace()
    import numpy as np

    def gridToNp(grid):
        if isinstance(grid, np.ndarray):
            return grid
        return np.array([[x == "O" for x in line] for line in grid], np.int8)

    history = [gridToNp(grid)]
    loadhistory = [calculateLoad(history[0])]

    def gridInHistory(npgrid):
        if not isinstance(npgrid, np.ndarray):
            npgrid = gridToNp(npgrid)
        for i, oldgrid in enumerate(history):
            if np.all(oldgrid == npgrid):
                return i
        return None

    cycles = 1000000000
    cycle = 0
    while cycle < cycles:
        grid = spinCycle(grid, printout=False)
        npgrid = gridToNp(grid)
        i = gridInHistory(npgrid)
        if i is not None:
            logger.debug(f"Cycle detected: {i}")
            cyclelen = cycle - i + 1
            ffwd = (cycles - i) % cyclelen
            historicalgrid = history[i + ffwd]
            return calculateLoad(historicalgrid)
        history.append(npgrid)
        loadhistory.append(calculateLoad(npgrid))
        cycle += 1
    return history[-1]


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
