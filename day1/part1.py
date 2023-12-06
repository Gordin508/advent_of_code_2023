#!/usr/bin/env python3
import sys


def main():
    # the program needs to read a multi-line input from stdin
    # we do not know the number of input lines in advance
    # so we read the input line by line until EOF
    userinput = sys.stdin.readlines()

    values = []
    for line in userinput:
        # each line contains a string of various characters and digits
        # get the first and last digit of each line
        digits = [int(d) for d in line if d.isdigit()]
        values.append(digits[0] * 10 + digits[-1])

    print("Sum: {}".format(sum(values)))


if __name__ == "__main__":
    main()
