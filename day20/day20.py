import logging
from enum import Enum, auto
import math


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Signal(Enum):
    LOW = auto()
    HIGH = auto()

    def invert(self):
        if self == Signal.LOW:
            return Signal.HIGH
        elif self == Signal.HIGH:
            return Signal.LOW

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


class SignalWrapper:
    def __init__(self, signal: Signal, target, source):
        self.signal = signal
        self.target = target
        self.source = source


class Module:
    def __init__(self, name):
        self.name = name
        self.targetmodules = []

    def handlesignal(self, signal, source):
        raise NotImplementedError()

    def addtargetmodule(self, module):
        self.targetmodules.append(module)
        module.addsourcemodule(self)

    def addsourcemodule(self, module):
        # only relevant for conjunction modules
        pass

    def __str__(self):
        targetmods = ", ".join((m.name for m in self.targetmodules))
        return f"{self.name} -> {targetmods}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class DummyModule(Module):
    def __init__(self, name):
        super().__init__(name)

    def handlesignal(self, signal, source):
        # just consume it
        return None


class BroadCaster(Module):

    def handlesignal(self, signal, source):
        return [SignalWrapper(signal, target, self) for target in self.targetmodules]


class FlipFlop(Module):
    def __init__(self, name):
        super().__init__(name)
        self.on = False

    def handlesignal(self, signal, source):
        if signal == Signal.LOW:
            self.on = not self.on
            newsignal = Signal.HIGH if self.on else Signal.LOW
            return [SignalWrapper(newsignal, target, self) for target in self.targetmodules]


class Conjunction(Module):
    def __init__(self, name):
        super().__init__(name)
        self.memory = {}
        self.activesignalsource = []
        self.queuedsignalsource = []
        self.activesignal = []
        self.queuedsignal = []

    def addsourcemodule(self, module):
        self.memory[module] = Signal.LOW

    def sendsignal(self, signal: Signal, source: Module):
        logger.debug(f"{source.name} -{signal}-> {self.name}")
        self.queuedsignal.append(signal)
        self.queuedsignalsource.append(source)

    def handlesignal(self, signal, source):
        self.memory[source] = signal
        newsignal = Signal.LOW if all((signal == Signal.HIGH for signal in self.memory.values())) else Signal.HIGH
        return [SignalWrapper(newsignal, target, self) for target in self.targetmodules]


def parsemodules(lines) -> dict[str, Module]:
    modules = {}
    targets = {}

    for line in lines:
        leftmodule, targetlist = line.split(" -> ")
        module = None
        match leftmodule[0]:
            case 'b':
                module = BroadCaster(leftmodule)
            case '%':
                module = FlipFlop(leftmodule[1:])
            case '&':
                module = Conjunction(leftmodule[1:])
        assert module is not None, f"{line}"
        modules[module.name] = module
        targets[module.name] = list((target.strip() for target in targetlist.split(", ") if len(target.strip()) > 0))

    # add dummy modules
    for names in targets.values():
        for name in names:
            if name not in modules:
                modules[name] = DummyModule(name)

    # add links between modules
    for module in modules.values():
        for target in targets.get(module.name, ()):
            targetmod = modules[target]
            module.addtargetmodule(targetmod)
    return modules


def part1(lines):
    modules = parsemodules(lines)
    button = DummyModule('button')
    logger.info(f"Parsed {len(modules)} modules")
    lowsignals = 0
    highsignals = 0

    def pushbutton():
        nonlocal lowsignals, highsignals
        queue = [SignalWrapper(Signal.LOW, modules['broadcaster'], button)]
        while queue:
            newq = []
            for entry in queue:
                if entry.signal == Signal.LOW:
                    lowsignals += 1
                elif entry.signal == Signal.HIGH:
                    highsignals += 1
                newpulses = entry.target.handlesignal(entry.signal, entry.source)
                if newpulses:
                    newq.extend(newpulses)

            queue = newq
    for _ in range(1000):
        pushbutton()

    return lowsignals * highsignals


def part2(lines):
    modules = parsemodules(lines)
    button = DummyModule('button')
    logger.info(f"Parsed {len(modules)} modules")
    lowsignals = 0
    highsignals = 0
    numpresses = 0
    assert 'rx' in modules
    rx_conj = next((m for m in modules.values() if any((target.name == 'rx') for target in m.targetmodules)))
    assert rx_conj is not None
    inputmodules = [m for m in modules.values() if any((target == rx_conj) for target in m.targetmodules)]
    cycles = {module.name: None for module in inputmodules}

    def pushbutton():
        nonlocal lowsignals, highsignals
        queue = [SignalWrapper(Signal.LOW, modules['broadcaster'], button)]
        while queue:
            newq = []
            for entry in queue:
                if entry.signal == Signal.LOW:
                    lowsignals += 1
                    if entry.target.name == 'rx':
                        return numpresses
                elif entry.signal == Signal.HIGH:
                    if entry.source in inputmodules and cycles[entry.source.name] is None:
                        cycles[entry.source.name] = numpresses
                        if all((value is not None for value in cycles.values())):
                            return math.lcm(*cycles.values())
                    highsignals += 1
                newpulses = entry.target.handlesignal(entry.signal, entry.source)
                if newpulses:
                    newq.extend(newpulses)

            queue = newq
    while True:
        numpresses += 1
        count = pushbutton()
        if count is not None:
            return count

    assert False


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
