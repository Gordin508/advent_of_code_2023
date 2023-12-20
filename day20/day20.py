import logging
from enum import Enum, auto


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


class Module:
    def __init__(self, name):
        self.queuedsignal = None
        self.activesignal = None
        self.targetmodules = []
        self.name = name

    def sendsignal(self, signal: Signal, source):
        assert signal is not None
        logger.debug(f"{source.name} -{signal}-> {self.name}")
        self.queuedsignal = signal

    def handlesignal(self):
        raise NotImplementedError()

    def numactivesignals(self):
        match self.activesignal:
            case Signal.LOW:
                return (1, 0)
            case Signal.HIGH:
                return (0, 1)
            case _:
                return (0, 0)

    def addtargetmodule(self, module):
        self.targetmodules.append(module)
        module.addsourcemodule(self)

    def addsourcemodule(self, module):
        # only relevant for conjunction modules
        pass

    def finishcycle(self):
        self.activesignal = self.queuedsignal
        self.queuedsignal = None

    def __str__(self):
        targetmods = ", ".join((m.name for m in self.targetmodules))
        return f"{self.name} -> {targetmods} (active: {self.activesignal}, queued: {self.queuedsignal})"

    def __repr__(self):
        return self.__str__()


class DummyModule(Module):
    def __init__(self, name):
        super().__init__(name)

    def handlesignal(self):
        # just consume it
        pass


class BroadCaster(Module):

    def handlesignal(self):
        if self.activesignal is not None:
            for target in self.targetmodules:
                target.sendsignal(self.activesignal, self)


class FlipFlop(Module):
    def __init__(self, name):
        super().__init__(name)
        self.on = False

    def handlesignal(self):
        if self.activesignal == Signal.LOW:
            self.on = not self.on
            for module in self.targetmodules:
                module.sendsignal(Signal.HIGH if self.on else Signal.LOW, self)


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

    def numactivesignals(self):
        lowsignals, highsignals = (0, 0)
        for signal in self.activesignal:
            if signal == Signal.LOW:
                lowsignals += 1
            elif signal == Signal.HIGH:
                highsignals += 1
        return (lowsignals, highsignals)

    def handlesignal(self):
        for signal, source in zip(self.activesignal, self.activesignalsource):
            self.memory[source] = signal
        if not self.activesignal:
            return
        newsignal = Signal.LOW if all((signal == Signal.HIGH for signal in self.memory.values())) else Signal.HIGH
        for module in self.targetmodules:
            module.sendsignal(newsignal, self)

    def finishcycle(self):
        self.activesignal = self.queuedsignal
        self.activesignalsource = self.queuedsignalsource
        self.queuedsignalsource = []
        self.queuedsignal = []


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
    import ipdb; ipdb.set_trace()
    modules = parsemodules(lines)
    button = DummyModule('button')
    logger.info(f"Parsed {len(modules)} modules")
    lowsignals = 0
    highsignals = 0

    def pushbutton():
        nonlocal lowsignals, highsignals
        modules['broadcaster'].sendsignal(Signal.LOW, button)
        modules['broadcaster'].finishcycle()
        activesignals = True
        while activesignals:
            activesignals = False
            for module in modules.values():
                low, high = module.numactivesignals()
                lowsignals += low
                highsignals += high
                if (low | high) > 0:
                    activesignals = True
                module.handlesignal()
            for module in modules.values():
                module.finishcycle()

    for _ in range(1000):
        pushbutton()

    return lowsignals * highsignals


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
