from collections import OrderedDict as _ODict


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


class ComputationPhase:
    def __init__(self, phase_id, cache, input, state, **kw):
        self.id = f"PHASE:{phase_id}"
        self.cache = cache
        self.input = input
        self.state = state

        """Cached default input obtained from inputspec.json file to reuse during multiple iterations"""
        self.input_args = FrozenDict(cache['input_args'])

        if not self.cache.get(self.id):
            self._initialize()
            self.cache[self.id] = True

    def _initialize(self):
        """Runs only once"""
        pass

    def compute(self):
        return {}

    def __str__(self):
        return f"{self.id}"


class PhaseEndWithSuccess(ComputationPhase):
    def compute(self):
        return {'success': True}


class PhasePipeline:
    def __init__(self, pipeline_id, cache, **kw):
        self.id = f"PIPELINE:{pipeline_id}"
        self.cache = cache

        if not cache.get(self.id):
            self._initialize()

        self.phases = _ODict()
        self.multi_iterations = {}
        self.local_only = {}

    def _initialize(self):
        """Runs only once"""
        self.cache[self.id] = {'index': 0, 'iterations': {}}

    def add_phase(self, phase_cls: ComputationPhase.__class__, local_only: bool = False,
                  multi_iterations: bool = False):
        """
        :param phase_cls: Custom implementation of ComputationPhase class
        :type phase_cls: ComputationPhase
        :param local_only: This phase will run only locally right after the previous phase is done.
        :type local_only: bool
        :param multi_iterations: Specifies if it is a multiple iterations phase.
        :type multi_iterations: bool
        Note: It is assumed that a normal(default) computation phase will run one round of local-remote.
        """
        self.phases[phase_cls.__name__] = phase_cls
        self.multi_iterations[phase_cls.__name__] = multi_iterations
        self.local_only[phase_cls.__name__] = local_only
        self.cache[self.id]['iterations'][phase_cls.__name__] = 0

    def __len__(self):
        return len(self.phases)

    @property
    def phase_ids(self):
        return list(self.phases.keys())

    def next_phase(self, jump_phase=False):
        current_phase_key = self.phase_ids[self.cache[self.id]['index']]
        self.cache[self.id]['iterations'][current_phase_key] += 1

        if jump_phase or not self.multi_iterations[current_phase_key]:
            if self.cache[self.id]['index'] < len(self.phases) - 1:
                self.cache[self.id]['index'] += 1

        return self.phase_ids[self.cache[self.id]['index']]

    def __str__(self):
        return [f"{id}" for id in self.phases]
