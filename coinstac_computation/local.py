from utils import PhasePipeline
import json
import sys


class Local:
    def __init__(
            self,
            computation_id: str,
            cache: dict = None, input: dict = None, state: dict = None,
            pipeline_cls=PhasePipeline,
            **shared_kw
    ):
        self.id = computation_id
        self.input = input
        self.state = state
        self.cache = cache
        self.out = {}

        self.phase_pipeline = None
        self.phase_pipeline = pipeline_cls(self.id, self.cache, self.input, self.state)
        if not self.cache.get(self.id):
            self._initialize()
            self.cache[self.id] = self.id

        self.args = {**shared_kw}
        if not self.cache.get('ARGS_PROCESSED'):
            self.cache.update(**self.input)

            """Update args"""
            for k in self.args:
                if self.cache.get(k) is None:
                    self.cache[k] = self.args[k]

            """Share args to remote"""
            self.out['args'] = {**self.args}
            for k in self.out['args'].keys():
                self.out['args'][k] = self.cache[k]

            self.cache['args'] = self.out['args']
            self.cache['ARGS_PROCESSED'] = True

    def _initialize(self):
        pass

    @property
    def num_phases(self):
        return len(self.phase_pipeline)

    @property
    def phase_ids(self):
        return self.phase_pipeline.phase_ids

    def compute(self, *args, **kwargs):

        self.out.update(**self.phase_pipeline.run())
        self.out['phase'] = self.input.get('phase', next(self.phase_pipeline))
        self.out.update(
            **self.phase_pipeline.phases[self.out['phase']].run()
        )
        return {"output": self.out}
