import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

strToIntMap = {word: num for (num, word) in enumerate("one two three four five six seven eight nine".split(), start=1)}


def convertToInt(match: str) -> int:
    assert len(match) > 0
    if len(match) == 1 and match.isdigit():
        return int(match)
    else:
        assert match in strToIntMap, f"{match} not in {strToIntMap}"
        return strToIntMap[match]


def part1(lines):
    # the program needs to read a multi-line input from stdin
    # we do not know the number of input lines in advance
    # so we read the input line by line until EOF

    values = []
    for line in lines:
        # each line contains a string of various characters and digits
        # get the first and last digit of each line
        digits = [int(d) for d in line if d.isdigit()]
        values.append(digits[0] * 10 + digits[-1])

    return sum(values)


def part2(lines):
    values = []
    matchRegex = r"(?=(one|two|three|four|five|six|seven|eight|nine|[0-9]))"
    matchRegex = re.compile(matchRegex)

    for line in lines:
        matches = matchRegex.finditer(line)
        results = [match.group(1) for match in matches]
        assert len(results) > 0
        matches = [results[0], results[-1]]
        convertedmatches = list(map(convertToInt, [matches[0], matches[-1]]))

        values.append(convertedmatches[0] * 10 + convertedmatches[-1])
        logger.debug(f"{line.strip()} ===> {results} ===> {convertedmatches}")
    return sum(values)


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
