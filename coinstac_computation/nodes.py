import json as _json
import sys as _sys

from .utils import PhasePipeline as _PhasePipeline


class COINSTACPyNode:
    _VALID_MODES_ = ['REMOTE', 'LOCAL']

    def __init__(self, mode: str, debug=False):
        self.out = {}
        self.cache = {}
        self.input = {}
        self._mode = mode.upper()
        self._pipeline = _PhasePipeline(self._mode, self.cache)
        self._debug = debug

        assert self._mode in COINSTACPyNode._VALID_MODES_, f"Not a valid node name: {self._mode}"

    def add_phase(self, phase_cls, multi_iterations=False):
        self._pipeline.add_phase(phase_cls, multi_iterations)

    def log(self, key='', **kw):
        for k, v in kw.items():
            print(f"\n{key} ### {self._mode} {k}: ", v)
            print("-" * 20)

    def compute(self, data):
        if self._debug:
            self.log('... pre ...', cache=self.cache, input=data['input'])

        if not self.cache.get('input_args'):
            """
            Save original input to save any computation arguments if present. 
            Some multiple iteration computations might need to reuse initial parameters.
            """
            self.cache['input_args'] = {**data['input']}

        self.cache['phase_key'] = self._pipeline.next_phase()

        phase = self._pipeline.phases[self.cache['phase_key']](
            self.cache['phase_key'], self.cache, data['input'], data['state']
        )
        phase_out = phase.compute()
        self.out.update(**phase_out)

        output = {"output": self.out, 'success': phase_out.get('success')}

        if self._debug:
            self.log('*** post ***', cache=self.cache, input=data['input'])
        return output

    def to_stdout(self):
        data = _json.loads(_sys.stdin.read())
        self.compute(data)
        output = {'output': self.out, 'cache': self.cache}
        try:
            output = _json.dumps(output)
            _sys.stdout.write(output)
        except Exception as e:
            raise Exception(f"Error parsing Json at {data['state']['clientId']} {e}:\n", output)
