import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Subset:
    def __init__(self, parent: str, rank: int):
        self.parent = parent
        self.rank = rank
        self.size = 1

    def __str__(self):
        return f"parent: {self.parent} rank: {self.rank} size: {self.size}"


def find(subsets, nodename):
    # find root and make root as parent of i
    # (path compression)
    if subsets[nodename].parent != nodename:
        subsets[nodename].parent = find(subsets, subsets[nodename].parent)

    return subsets[nodename].parent


def Union(subsets, set1, set2):
    root1 = find(subsets, set1)
    root2 = find(subsets, set2)

    # Attach smaller rank tree under root of high
    # rank tree (Union by Rank)
    if subsets[root1].rank < subsets[root2].rank:
        subsets[root1].parent = root2
        subsets[root2].size += subsets[root1].size
    elif subsets[root1].rank > subsets[root2].rank:
        subsets[root2].parent = root1
        subsets[root1].size += subsets[root2].size

    # If ranks are same, then make one as root and
    # increment its rank by one
    else:
        subsets[root2].parent = root1
        subsets[root1].size += subsets[root2].size
        subsets[root1].rank += 1


def MinCut(V, E):
    # Karger's algorithm

    subsets = {v: Subset(v, 0) for v in V}
    vertices = len(V)
    cutedges = set()
    while vertices > 2:
        src, dest = random.choice(list(E))
        subset1 = find(subsets, src)
        subset2 = find(subsets, dest)
        if subset1 == subset2:
            continue

        # contract edge
        Union(subsets, subset1, subset2)
        vertices -= 1

    for e in E:
        subset1 = find(subsets, e[0])
        subset2 = find(subsets, e[1])
        if subset1 != subset2:
            cutedges.add(e)
    result = 1
    if len(cutedges) == 3:
        for origin, ss in subsets.items():
            if ss.parent == origin:
                result *= ss.size
    return result, cutedges


def part1(lines):
    V = set()
    E = set()

    for line in lines:
        left, *right = line.replace(':', '').split()
        name = left.strip()
        if not name:
            continue
        V.add(name)
        for othernode in right:
            othername = othernode.strip()
            if not othername:
                continue
            V.add(othername)
            E.add((name, othername) if name < othername else (othername, name))
    cutedges = None
    result = None
    while not cutedges or len(cutedges) != 3:
        result, cutedges = MinCut(V, E)
    logger.info(cutedges)
    return result


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
