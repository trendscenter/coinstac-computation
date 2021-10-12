from utils import PhasePipeline


class Local:
    def __init__(
            self,
            computation_id: str,
            phase_pipeline: PhasePipeline,
            cache: dict = None, input: dict = None, state: dict = None,
            **shared_kw
    ):
        self.id = computation_id
        self.input = input
        self.state = state
        self.cache = cache
        self.out = {}

        self.args = {**shared_kw}
        if not self.cache.get('ARGS_PROCESSED'):
            self.cache.update(**self.input)

            """Update args"""
            for k in self.args:
                if self.cache.get(k) is None:
                    self.cache[k] = self.args[k]

            """Share args to remote"""
            self.out['args'] = {**self.args}
            for k in self.out['args']:
                self.out['args'][k] = self.cache[k]

            self.cache['args'] = self.out['args']
            self.cache['ARGS_PROCESSED'] = True

        if not self.cache.get(self.id):
            self.phase_pipeline = phase_pipeline
            self.out.update(**phase_pipeline.run())
            self.cache[self.id] = True

    def add_phase(self, phase):
        self.phase_pipeline.add_phase(phase)

    def compute(self, *args, **kwargs):
        self.out['phase'] = self.input.get('phase', next(self.phase_pipeline))
        self.out.update(**self.phase_pipeline.phases[self.out['phase']].run())
        return {"output": self.out}
