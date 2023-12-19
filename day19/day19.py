import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PARTREGEX = re.compile(r"(?P<attr>[xmas])=(?P<value>\d+)")
WORKFLOWREGEX = re.compile(r"(?P<name>\w+)\{(?P<instructions>[^\}]*)\}")
INSTRUCTIONREGEX = re.compile(r"((?P<condition>[^:]+):)?(?P<action>([a-z]+|[AR]))")


class Part:
    def __init__(self, x: int = 0, m: int = 0, a: int = 0, s: int = 0):
        self.x = int(x)
        self.m = int(m)
        self.a = int(a)
        self.s = int(s)

    @classmethod
    def from_line(cls, line):
        kwargs = {match['attr']: match['value'] for match in PARTREGEX.finditer(line)}
        return cls(**kwargs)

    def get(self, attr: str):
        assert attr in "xmas"
        return self.__getattribute__(attr)

    def value(self):
        return self.x + self.m + self.a + self.s

    def __str__(self):
        return f"{{x: {self.x}, m: {self.m}, a: {self.a}, s: {self.s}}}"

    def __repr__(self):
        return self.__str__()


class Instruction:
    def __init__(self, attr: str, op: str, value: int, action: str):
        if attr is not None:
            assert attr in "xmas"
        if op is not None:
            assert op in "<>"
        assert not ((attr is None) ^ (op is None))
        self.attr = attr
        self.op = op
        self.value = int(value) if value is not None else None
        self.action = action

    def test(self, part: Part):
        if self.attr:
            match self.op:
                case "<":
                    return part.get(self.attr) < self.value
                case ">":
                    return part.get(self.attr) > self.value
                case _:
                    assert False, f"{self.op}"
        else:
            return True

    def __str__(self):
        if not self.attr:
            return f"{self.action}"
        return f"{self.attr}{self.op}{self.value}:{self.action}"

    def __repr__(self):
        return self.__str__()


class Workflow:
    def __init__(self, name, instructions: [Instruction]):
        self.instructions = instructions
        self.name = name

    @classmethod
    def from_line(cls, line):
        line = line.strip()
        assert line
        instructions = []
        match = WORKFLOWREGEX.match(line)
        if match is None:
            pass
        assert match is not None, f"{line}"
        name = match['name']
        for instr in match['instructions'].split(','):
            imatch = INSTRUCTIONREGEX.match(instr)
            gdict = imatch.groupdict()
            action = imatch['action']
            if gdict.get('condition', None):
                condition = gdict['condition'].replace(' ', '')
                attr = condition[0]
                op = condition[1]
                val = int(condition[2:])
                instructions.append(Instruction(attr, op, val, action))
            else:
                instructions.append(Instruction(None, None, None, action=action))
        return Workflow(name, instructions)

    def execute(self, part):
        assert len(self.instructions) > 0
        for instr in self.instructions:
            if instr.test(part):
                return instr.action
        assert False, "Should never happen"

    def __str__(self):
        return f"{self.name}" + ",".join((str(i) for i in self.instructions))

    def __repr__(self):
        return self.__str__()


def parseInput(lines):
    workflows = {}
    parts = []

    parsing = "w"
    for line in lines:
        if len(line.strip()) == 0:
            parsing = "p"
            continue
        match parsing:
            case "w":
                workflow = Workflow.from_line(line)
                workflows[workflow.name] = workflow
            case "p":
                parts.append(Part.from_line(line))
    return (workflows, parts)


def part1(lines):
    workflows, parts = parseInput(lines)
    assert 'in' in workflows
    result = 0
    for part in parts:
        action = 'in'
        while action not in ["A", "R"]:
            assert action in workflows, f"{action}"
            workflow = workflows[action]
            action = workflow.execute(part)
        match action:
            case "A":
                result += part.value()
            case "R":
                pass
            case _:
                assert False, f"{action}"
    return result


class Constraint:
    def __init__(self, attr, op, value):
        self.attr = attr
        self.op = op
        self.value = value

    @classmethod
    def from_instr(cls, instruction: Instruction, invert=False):
        if not instruction.attr:
            return None
        op = instruction.op
        value = instruction.value
        if invert:
            op = "<" if instruction.op == ">" else ">"
            value = value + 1 if instruction.op == ">" else value - 1
        return Constraint(instruction.attr, op, value)

    def __str__(self):
        return f"{self.attr}{self.op}{self.value}"

    def __repr__(self):
        return self.__str__()


class Constraints:
    def __init__(self):
        self.constraints = []

    def addConstraint(self, instruction: Instruction, invert=False):
        newc = Constraint.from_instr(instruction, invert)
        if newc:
            self.constraints.append(newc)

    def copy(self):
        newc = Constraints()
        newc.constraints = self.constraints.copy()
        return newc

    def solve(self) -> int:
        possibilities = 1
        for attr in ('xmas'):
            const = (c for c in self.constraints if c.attr == attr)
            interval = [1, 4000]
            for c in const:
                if c.op == "<":
                    interval[1] = min(interval[1], c.value - 1)
                elif c.op == ">":
                    interval[0] = max(interval[0], c.value + 1)
                if interval[1] < interval[0]:
                    return 0
            possibilities *= max(0, interval[1] - interval[0] + 1)
        return possibilities

    def solvable(self) -> bool:
        return self.solve() > 0

    def __str__(self):
        return f"{len(self.constraints)} constraints: {self.constraints}"

    def __repr__(self):
        return self.__str__()


def part2(lines):
    workflows, _ = parseInput(lines)

    # BFS
    class QueueEntry:
        def __init__(self, action, constraints):
            self.action = action
            self.constraints = constraints

        def __str__(self):
            return f"{self.action} ({self.constraints})"

        def __repr__(self):
            return self.__str__()

    queue = [QueueEntry('in', Constraints())]
    possibilities = 0

    while queue:
        newq = []
        for entry in queue:
            if not entry.constraints.solvable():
                continue
            if entry.action == "R":
                continue
            if entry.action == "A":
                possibilities += entry.constraints.solve()
                continue
            workflow = workflows[entry.action]
            runningconstraints = entry.constraints.copy()
            for instr in workflow.instructions:
                if instr.attr:
                    newc = runningconstraints.copy()
                    newc.addConstraint(instr)
                    newq.append(QueueEntry(instr.action, newc))
                    runningconstraints.addConstraint(instr, invert=True)
                else:
                    newq.append(QueueEntry(instr.action, runningconstraints))
        queue = newq

    return possibilities


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
