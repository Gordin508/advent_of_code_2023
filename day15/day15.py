import logging
from collections import OrderedDict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def hash(hashstr: str) -> int:
    hash = 0
    for character in ((x for x in hashstr.strip() if x != "\n")):
        ascii = ord(character)  # we trust this is ascii
        assert ascii < 128, f"Unexpected char: {character}"
        hash = ((hash + ascii) * 17) % 256
    return hash


def part1(lines):
    assert len(lines) == 1
    result = sum((hash(step.strip()) for step in lines[0].split(",")))
    return result


class Box:
    def __init__(self, boxnumber):
        self.number = boxnumber
        self.lenses = OrderedDict()

    def addLens(self, label, strength):
        self.lenses[label] = strength

    def removeLens(self, label):
        self.lenses.pop(label, None)

    def empty(self):
        return len(self.lenses) == 0

    def __str__(self):
        return f"Box {self.number}: " + " ".join((f"[{label} {strength}]" for (label, strength) in self.lenses.items()))

    def __repr__(self):
        return self.__str__()

    def focusPower(self):
        return (self.number + 1) * sum((i * strength for (i, strength) in enumerate(self.lenses.values(), start=1)))


def part2(lines):
    assert len(lines) == 1
    boxes = {}
    for step in lines[0].split(","):
        step = step.strip()
        if "-" in step:
            label, strength = step.split("-")
            labelhash = hash(label)

            # emulate defaultdict-like behavior
            boxes[labelhash] = boxes.get(labelhash, Box(labelhash))

            boxes[labelhash].removeLens(label)
        elif "=" in step:
            label, strength = step.split("=")
            strength = int(strength)
            labelhash = hash(label)

            # emulate defaultdict-like behavior
            boxes[labelhash] = boxes.get(labelhash, Box(labelhash))

            boxes[labelhash].addLens(label, strength)
        else:
            assert False, f"{step} malformed"
    return sum((box.focusPower() for box in boxes.values()))


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
