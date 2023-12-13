import logging
import sys
import re
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)




STRENGTHS = ['A', 'K', 'Q', 'T', '9', '8', '7', '6', '5', '4', '3', '2', 'J']
STRENGTHS = {l: x for (l, x) in zip(STRENGTHS[::-1], range(len(STRENGTHS)))}


class Card:
    def __init__(self, letter):
        assert len(letter) == 1
        self.letter = letter

    def isjoker(self):
        return self.letter == "J"

    def __gt__(self, other):
        return STRENGTHS[self.letter] > STRENGTHS[other.letter]

    def __lt__(self, other):
        return STRENGTHS[self.letter] < STRENGTHS[other.letter]

    def __eq__(self, other):
        return STRENGTHS[self.letter] == STRENGTHS[other.letter]

    def __str__(self):
        return self.letter

    def __repr__(self):
        return self.__str__()


class HandType(Enum):
    FIVEOFAKIND = 1
    FOUROFAKIND = 2
    FULLHOUSE = 3
    THREEOFAKIND = 4
    TWOPAIR = 5
    ONEPAIR = 6
    HIGHCARD = 7

    def __gt__(self, other):
        return self.value < other.value

    def __lt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    @classmethod
    def from_cards(cls, cards):
        assert len(cards) == 5
        from collections import Counter
        counts = Counter(cards)
        values = list(counts.values())
        maxvalue = max(values)
        match maxvalue:
            case 5: return cls.FIVEOFAKIND
            case 4: return cls.FOUROFAKIND
        if 3 in values:
            if 2 in values:
                return cls.FULLHOUSE
            else:
                return cls.THREEOFAKIND
        if len([x for x in values if x == 2]) == 2:
            return cls.TWOPAIR
        if 2 in values:
            return cls.ONEPAIR
        return cls.HIGHCARD

    @classmethod
    def from_cards_with_jokers(cls, cards):
        assert len(cards) == 5
        from collections import Counter
        counts = Counter(cards)
        numjokers = counts['J']
        del counts['J']
        values = list(counts.values())
        if numjokers == 0:
            return cls.from_cards(cards)

        maxvalue = max(values) if len(values) > 0 else 0
        match maxvalue + numjokers:
            case 5: return cls.FIVEOFAKIND
            case 4: return cls.FOUROFAKIND
        twomostcommon = sum((count for (_, count) in counts.most_common(2)))
        if twomostcommon >= 5 - numjokers:
            return cls.FULLHOUSE
        if maxvalue + numjokers >= 3:
            return cls.THREEOFAKIND

        # twopair
        if twomostcommon + numjokers >= 4:
            return cls.TWOPAIR
        # onepair
        if maxvalue + numjokers >= 2:
            return cls.ONEPAIR

        return cls.HIGHCARD

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Hand:
    def __init__(self, cards, bid, jokers: bool = False):
        self.bid = int(bid)
        self.cards = [Card(card) for card in cards]
        self.type = HandType.from_cards(cards) if not jokers else HandType.from_cards_with_jokers(cards)

    def __str__(self):
        cardstring = "".join((str(card) for card in self.cards))
        return f"{cardstring}: type {self.type} (bid {self.bid})"

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        try:
            if self.type != other.type:
                return -1 if self.type < other.type else 1
        except:
            import ipdb; ipdb.set_trace()
        for owncard, othercard in zip(self.cards, other.cards):
            if owncard < othercard:
                return -1
            elif owncard > othercard:
                return 1
        return 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __eq__(self, other):
        return self.__cmp__(other) == 0


def parseinput(lines, jokers=False):
    hands = []
    for line in lines:
        match = re.match(r'(?P<hand>[AKQJT2-9]+)\s+(?P<bid>\d+)\n?', line)
        cards = match.group('hand')
        bid = int(match.group('bid'))
        hands.append(Hand(cards, bid, jokers=jokers))
    return hands


def part1(lines):
    global STRENGHTS
    STRENGTHS = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
    STRENGTHS = {l: x for (l, x) in zip(STRENGTHS[::-1], range(len(STRENGTHS)))}
    hands = sorted(parseinput(lines))
    logger.info(f"Created {len(hands)} hands")
    # logger.info(f"{hands}")

    totalvalue = sum((hand.bid * rank for (hand, rank) in zip(hands, range(1, len(hands) + 1))))
    logger.info(f"Part 1: {totalvalue}")


def part2(lines):
    hands = sorted(parseinput(lines, jokers=True))
    logger.info(f"Created {len(hands)} hands")
    # logger.info(f"{hands}")

    totalvalue = sum((hand.bid * rank for (hand, rank) in zip(hands, range(1, len(hands) + 1))))
    logger.info(f"Part 2: {totalvalue}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
