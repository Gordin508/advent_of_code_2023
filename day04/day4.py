import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Card:
    def __init__(self, line):
        match = re.match(r"Card\s+(?P<cardid>\d+): (?P<winning>[\d\s]+)\s*\|\s*(?P<have>[\d\s]+)", line.strip())
        if match is None:
            logger.error(f"{line}")
            exit(1)
        self.id = int(match.group('cardid'))
        self.winning = set((int(x) for x in re.findall(r"\d+", match.group('winning'))))
        self.have = set((int(x) for x in re.findall(r"\d+", match.group('have'))))
        self.copies = 1

    def winningNumbers(self):
        return len(self.winning.intersection(self.have))

    def value(self):
        havewinning = self.winningNumbers()
        return 2**(havewinning - 1) if havewinning > 0 else 0

    def __str__(self):
        return f"Card {self.id}: Winning Numbers: {self.winning} | Have: {self.have}"


def part1(lines):
    totalvalue = 0
    for line in lines:
        card = Card(line)
        logger.debug(card)
        totalvalue += card.value()
    logger.info(f"Part 1: {totalvalue}")


def part2(lines):
    cards = [Card(line) for line in lines]
    for card in cards:
        correct = card.winningNumbers()
        for c in cards[card.id:card.id + correct]:
            c.copies += card.copies

    numcards = sum((c.copies for c in cards))
    logger.info(f"Part 2: {numcards}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
