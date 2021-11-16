from collections import OrderedDict

from iterator import Iterator as _Iter


def check(logic, k, v, kw):
    phases = []
    for site_vars in kw.values():
        phases.append(site_vars.get(k) == v)
    return logic(phases)


class FrozenDict(dict):
    def __init__(self, _dict):
        super().__init__(_dict)

    def prompt(self, key, value):
        raise ValueError(f'*** '
                         f'Attempt to modify frozen dict '
                         f'[{key} : {self[key]}] with [{key} : {value}]'
                         f' ***')

    def __setitem__(self, key, value):
        if key not in self:
            super(FrozenDict, self).__setitem__(key, value)
        else:
            self.prompt(key, value)

    def update(self, **kw):
        for k, v in kw.items():
            self[k] = v


class Phase:
    def __init__(self, phase_id, cache, input, state):
        self._id = f"PHASE:{phase_id}"

        self.cache = cache
        self.input = input
        self.state = state

        if not self.cache.get(self._id):
            self._initialize()
            self.cache[self._id] = True

    def _initialize(self):
        pass

    def run(self):
        return {}

    def __str__(self):
        return f"{self._id}"


class PhasePipeline(_Iter):
    def __init__(self, pipeline_id, cache, input, state, **kw):
        self._id = f"PHASE-PIPE:{pipeline_id}"

        super().__init__(cache=cache, **kw)
        self.input = input
        self.state = state

        if not self.cache.get(self._id):
            self._initialize()
            self.cache[self._id] = True

        self.phases = OrderedDict()
        self.end = 0

    def _initialize(self):
        pass

    def add_phase(self, phase: Phase):
        self.phases[phase._id] = phase
        self.end += 1

    def __len__(self):
        return len(self.phases)

    @property
    def phase_ids(self):
        return list(self.phases.keys())

    def run(self):
        return {}

    def __next__(self):
        self.run()
        nxt = next(self)
        return self.phase_ids[nxt['i']], nxt

    def __str__(self):
        return [f"{id}" for id in self.phases]
