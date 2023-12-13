import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def part1(lines):
    pass


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
