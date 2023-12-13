import logging
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Node:
    def __init__(self, name, left, right):
        assert max((len(s) for s in [name, left, right])) == 3
        assert min((len(s) for s in [name, left, right])) == 3
        self.name = name
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.name}: {self.left} {self.right}"

    def __repr__(self):
        return self.__str__()

    def isstartnode(self):
        return self.name[-1] == 'A'

    def isendnode(self):
        return self.name[-1] == 'Z'


def parseinput(lines):
    movesequence = lines[0].strip()
    lines = lines[2:]
    nodes = {}
    for line in lines:
        match = re.match(r"(?P<node>[\w]{3}) = \((?P<left>[\w]{3}), (?P<right>[\w]{3})\)", line.strip())
        assert match is not None
        node = Node(name=match.group('node'), left=match.group('left'), right=match.group('right'))
        nodes[node.name] = node
    return (movesequence, nodes)


def part1(lines):
    movesequence, nodes = parseinput(lines)
    # logger.info(f"{nodes}")

    node = nodes.get('AAA', None)
    if node is None:
        logger.debug("Currently running against an input for part 2")
        return

    def goleft(node):
        return nodes[nodes[node.name].left]

    def goright(node):
        return nodes[nodes[node.name].right]

    steps = 0
    while (node.name != 'ZZZ'):
        for move in movesequence:
            if move == 'L':
                node = goleft(node)
            else:
                node = goright(node)
            steps += 1
    logger.info(f"Part 1: {steps}")


def gcdb(a, b):
    while b > 0:
        a, b = b, a % b
    return a


def gcd(numbers):
    from functools import reduce
    return reduce(gcdb, numbers)


def lcm(numbers):
    def lcma(a, b):
        return a * b // gcdb(a, b)
    from functools import reduce
    return reduce(lcma, numbers)


def part2(lines):
    movesequence, nodes = parseinput(lines)
    # logger.info(f"{nodes}")

    nodelist = [node for node in nodes.values() if node.isstartnode()]

    def goleft(nodelist):
        return [nodes[nodes[node.name].left] for node in nodelist]

    def goright(nodelist):
        return [nodes[nodes[node.name].right] for node in nodelist]

    steps = 0
    moduli = [-1]*len(nodelist)
    while not all((m >= 0 for m in moduli)):
        move = movesequence[steps % len(movesequence)]
        if move == 'L':
            nodelist = goleft(nodelist)
        else:
            nodelist = goright(nodelist)
        steps += 1
        logger.debug(f"{nodelist}")
        # check which nodes have reached the target
        for i, node in enumerate(nodelist):
            if moduli[i] >= 0:
                continue
            if node.isendnode():
                moduli[i] = steps
    assert min(moduli) >= 0
    moduli = [x for x in moduli if x > 0]
    result = lcm(moduli)
    logger.info(f"Part 2: {result}")


def main():
    infile = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(infile) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
