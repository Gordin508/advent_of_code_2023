import logging
import sys
import re
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SeedRange:
    def __init__(self, source, dest, rangelen):
        self.source = int(source)
        self.dest = int(dest)
        self.rangelen = int(rangelen)
        self.sourceend = self.source + self.rangelen - 1

    def __str__(self):
        return f"{self.source} --> {self.dest} (range: {self.rangelen})"

    def __repr__(self):
        return str(self)

    def contains_src(self, source):
        return source >= self.source and source < self.source + self.rangelen

    def contains_dest(self, dest):
        return dest >= self.dest and dest < self.dest + self.rangelen

    def map_forward(self, source):
        if not self.contains_src(source):
            return None
        return self.dest + (source - self.source)

    def map_backward(self, dest):
        if not self.contains_dest(dest):
            return None
        return self.source + (dest - self.dest)

    def intersect(self, sourcestart, sourceend):
        assert sourcestart <= sourceend
        return (sourcestart <= self.sourceend and sourceend >= self.source) or (sourcestart >= self.source and sourcestart <= self.sourceend)

    def maprange(self, sourcestart, sourceend):
        if not self.intersect(sourcestart, sourceend):
            return None
        sourcestart = max(sourcestart, self.source)
        sourceend = min(sourceend, self.sourceend)
        return (self.map_forward(sourcestart), self.map_forward(sourceend))



class ThingToThingMap:
    def __init__(self, lines):
        lines = [line.strip() for line in lines]
        match = re.match(r'(?P<from>\w+)\-to\-(?P<to>\w+) map:', lines[0])
        self.from_ = match.group('from')
        self.to = match.group('to')
        self.edges_incoming = list()
        self.edges_outgoing = list()

        lines = lines[1:]
        self.ranges = []
        for line in lines:
            if len(line) == 0:
                break
            match = re.match(r"(?P<dest>\d+)\s+(?P<source>\d+)\s+(?P<rangelen>\d+)", line)
            assert match is not None
            self.ranges.append(SeedRange(match.group('source'), match.group('dest'), match.group('rangelen')))

        self.ranges = list(sorted(self.ranges, key=lambda r: r.source))


    def map_forward(self, source):
        relevant_range = next((r for r in self.ranges if r.contains_src(source)), None)
        return source if relevant_range is None else relevant_range.map_forward(source)

    def map_range_forward(self, sourcestart, sourceend):
        assert sourcestart <= sourceend
        if sourcestart == sourceend:
            mapped = self.map_forward(sourcestart)
            return [(mapped, mapped)]

        if len(self.ranges) == 0 or sourceend < self.ranges[0].source or sourcestart > self.ranges[-1].sourceend:
            return [(sourcestart, sourceend)]
        idx = 0
        while idx < len(self.ranges) and not (self.ranges[idx].intersect(sourcestart, sourceend)):
            idx += 1
        out = []
        lower = sourcestart
        upper = sourceend
        while (lower <= upper):
            if idx >= len(self.ranges):
                out.append((lower, upper))
                break
            r = self.ranges[idx]
            if r.source > lower:
                out.append((lower, min(r.source - 1, upper)))
                lower = r.source
            if lower >= upper:
                break
            out.append(r.maprange(lower, upper))
            lower = min(upper, r.sourceend + 1)
            if lower >= upper:
                break
            idx += 1
        return out

    def __str__(self):
        out = ""
        out += f"Map: {self.from_} --> {self.to} ({len(self.ranges)} entries):\n"
        for r in self.ranges:
            out += str(r) + "\n"

        return out

    def __repr__(self):
        return str(self)


def buildGraph(maps):
    destination = defaultdict(list)
    for map in maps:
        destination[map.from_].append(map)
    for map in maps:
        map.edges_outgoing = [m for m in destination[map.to]]
        for destmap in map.edges_outgoing:
            destmap.edges_incoming.append(map)


def parseMaps(lines):
    seeds = re.findall(r'\d+', lines[0])
    seeds = [int(seed) for seed in seeds]
    lines = [line.strip() for line in lines[2:]]
    i = 1
    mapstart = 0
    maps = []
    while (i <= len(lines)):
        if i >= len(lines) or lines[i].endswith("map:"):
            # block finished
            maps.append(ThingToThingMap(lines[mapstart:i]))
            mapstart = i
        i += 1
    logger.info(f"Parsed {len(maps)} maps")
    return seeds, maps


def findLowestLocation1(seeds, maps):
    mapdict = {map.from_: map for map in maps}
    locations = []
    for seed in seeds:
        srcmap = mapdict['seed']
        val = seed
        # print(f"{srcmap.from_} {val}, ", end="")
        while (srcmap.to != 'location'):
            val = srcmap.map_forward(val)
            srcmap = mapdict[srcmap.to]
            # print(f"{srcmap.from_} {val}, ", end="")
        locations.append(srcmap.map_forward(val))
        # print(f"location {locations[-1]}")

    return min(locations)


def findLowestLocation2(seeds, maps):
    # bfs over maps
    mapdict = {map.from_: map for map in maps}
    locations = []
    for seed, rangelen in zip(seeds[0::2], seeds[1::2]):
        srcmap = mapdict['seed']
        val = [(seed, seed + rangelen - 1)]
        # print(f"{srcmap.from_} {val}, ", end="")
        while (srcmap.to != 'location'):
            val = [srcmap.map_range_forward(sourcestart, sourceend) for (sourcestart, sourceend) in val]
            val = [r for sublist in val for r in sublist]  # flatten
            srcmap = mapdict[srcmap.to]
            # print(f"{srcmap.from_} {val}, ", end="")
        locationranges = [srcmap.map_range_forward(sourcestart, sourceend) for (sourcestart, sourceend) in val]
        locationranges = [r for sublist in locationranges for r in sublist]
        locations.append(min((start for (start, _) in locationranges)))

    return min(locations)


def part1(lines):
    seeds, maps = parseMaps(lines)
    buildGraph(maps)
    logger.info(f"Part 1: {findLowestLocation1(seeds, maps)}")


def part2(lines):
    seeds, maps = parseMaps(lines)
    buildGraph(maps)
    logger.info(f"Part 2: {findLowestLocation2(seeds, maps)}")


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    with open(input_file) as f:
        lines = f.readlines()
    part1(lines)
    part2(lines)


if __name__ == '__main__':
    main()
