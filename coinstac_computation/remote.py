from utils import FrozenDict, PhasePipeline, check


class Remote:
    def __init__(self, computation_id: str, phase_pipeline: PhasePipeline,
                 cache: dict = None, input: dict = None, state: dict = None):
        self.id = computation_id
        self.input = input
        self.state = state
        self.cache = cache

        self.args = FrozenDict(
            self.cache.setdefault('args', self.input)
        )

        self.out = {}

        if not self.cache.get('args'):
            site = list(self.input.values())[0]
            self.cache.update(**site['args'])
            self.cache['args'] = True

        if not self.cache.get(self.id):
            self.phase_pipeline = phase_pipeline
            self.phase_pipeline.run()
            self.cache[self.id] = True

    def add_phase(self, phase):
        self.phase_pipeline.add_phase(phase)

    @property
    def num_phases(self):
        return len(self.phase_pipeline)

    @property
    def phase_ids(self):
        return self.phase_pipeline.phase_ids

    def compute(self, *args, **kwargs):
        self.out['phase'] = self.input.get('phase', next(self.phase_pipeline))
        self.out.update(**self.phase_pipeline.phases[self.out['phase']].run())
        return {"output": self.out, "success": check(all, 'success', True, self.input)}
