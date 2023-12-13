import logging
import sys
import re
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parseinput(lines):
    numbers = []
    for line in lines:
        nums = [int(n) for n in line.strip().split()]
        numbers.append(nums)
    return np.array(numbers, dtype=np.int64)


def solve(lines, backward = False):
    history = parseinput(lines)
    logger.info(f"Input shape: {history.shape}")
    extrapolated = np.empty(history.shape[0], dtype=np.int64)
    for i, row in enumerate(history):
        stack = [row]
        while not np.all(stack[-1] == 0):
            stack.append(stack[-1][1:] - stack[-1][:-1])
        assert min((len(entry) for entry in stack)) > 0
        if len(stack) == 1:
            extrapolated[i] = 0
            continue
        if not backward:
            stack[-1] = np.concatenate((stack[-1], np.array([0])))
            for idx in range(len(stack) - 2, -1, -1):
                stack[idx] = np.concatenate((stack[idx], np.array([stack[idx + 1][-1] + stack[idx][-1]])))
            extrapolated[i] = stack[0][-1]
        else:
            stack[-1] = np.concatenate((np.array([0]), stack[-1]))
            for idx in range(len(stack) - 2, -1, -1):
                stack[idx] = np.concatenate((np.array([-stack[idx + 1][0] + stack[idx][0]]), stack[idx]))
            extrapolated[i] = stack[0][0]

    return extrapolated


def part1(lines):
    extrapolated = solve(lines)
    logger.info(f"Part 1: {extrapolated.sum()}")


def part2(lines):
    extrapolated = solve(lines, backward=True)
    logger.info(f"Part 2: {extrapolated.sum()}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
