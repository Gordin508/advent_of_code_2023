import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def tiltnorth(grid):
    for y, line in enumerate(grid):
        for x, tile in enumerate(line):
            # if there is a rounded rock, move it north till it hits an obstacle
            match tile:
                case "O":
                    destination = y
                    while destination > 0 and grid[destination - 1][x] == ".":
                        destination -= 1
                    grid[y][x] = "."
                    grid[destination][x] = "O"  # can equal y
                case _:
                    continue


def calculateLoad(grid):
    total = 0
    for y, line in enumerate(grid):
        loadfactor = len(grid) - y
        total += loadfactor * len([tile for tile in line if tile == "O"])
    return total


def part1(lines):
    grid = [list(line.strip()) for line in lines]
    assert min((len(line) for line in grid)) == max((len(line) for line in grid))

    tiltnorth(grid)

    return calculateLoad(grid)


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
