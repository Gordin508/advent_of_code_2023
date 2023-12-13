#!/usr/bin/env python3
import sys
import re

strToIntMap = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9
}


def main():
    # the program needs to read a multi-line input from stdin
    # we do not know the number of input lines in advance
    # so we read the input line by line until EOF
    # userinput = sys.stdin.readlines()
    inputfile = "input.txt" if len(sys.argv) == 0 else sys.argv[1]
    with open(inputfile, 'r') as inputtxt:
        userinput = inputtxt.readlines()

    matchRegex = r"(one|two|three|four|five|six|seven|eight|nine|[0-9])"
    matchRegex = re.compile(matchRegex)

    def convertToInt(match: str) -> int:
        assert len(match) > 0
        if len(match) == 1 and match.isdigit():
            return int(match)
        else:
            assert match in strToIntMap
            return strToIntMap[match]

    values = []
    for line in userinput:
        # each line contains a string of various characters and digits
        # get the first and last digit of each line
        # matches = matchRegex.findall(line)
        matches = re.finditer(r'(?=(one|two|three|four|five|six|seven|eight|nine|[0-9]))', line)
        results = [match.group(1) for match in matches]
        assert len(results) > 0
        matches = [results[0], results[-1]]
        convertedmatches = list(map(convertToInt, [matches[0], matches[-1]]))

        values.append(convertedmatches[0] * 10 + convertedmatches[-1])
        print(f"{line.strip()} ===> {results} ===> {convertedmatches}")

    print("Sum: {}".format(sum(values)))


if __name__ == "__main__":
    main()
