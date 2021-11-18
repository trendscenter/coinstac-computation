import json as _json
import sys as _sys
import traceback as _tb
import copy as _copy

from .utils import PhasePipeline as _PhasePipeline, FrozenDict as _FrozenDict


class COINSTACPyNode:
    _VALID_MODES_ = ['REMOTE', 'LOCAL']

    def __init__(self, mode: str, debug=False):
        self.cache = {}
        self._mode = mode.upper()
        self._pipeline = _PhasePipeline(self._mode, self.cache)
        self.debug = debug
        self.logs = {}

        assert self._mode in COINSTACPyNode._VALID_MODES_, f"Not a valid node name: {self._mode}"

    def add_phase(self, phase_cls, multi_iterations=False):
        self._pipeline.add_phase(phase_cls, multi_iterations)

    def print_logs(self):
        for k, v in self.logs.items():
            print(f"{'-' * 3}{k.upper()}{'-' * 50}")
            for k1, v1 in v.items():
                print(f"\t[ {k1} ] -> {v1}")
        print()

    def compute(self, data):
        if self.debug:
            self.logs['input'] = {}
            self.logs['input']['PRE-COMPUTATION '] = _copy.deepcopy(data)
            self.logs['cache'] = {}
            self.logs['cache']['PRE-COMPUTATION '] = _copy.deepcopy(self.cache)

        if not self.cache.get('input_args'):
            """Some multi-iteration computations might need to reuse initial parameters, so save it."""
            self.cache['input_args'] = _FrozenDict(_copy.deepcopy(data['input']))

        phase_key = self.cache.get('next_phase')
        if not phase_key:
            phase_key = self._pipeline.next_phase()

        phase = self._pipeline.phases[phase_key](
            phase_key,
            self.cache, data['input'], data['state']
        )

        phase_out = phase.compute()
        if not phase_out:
            phase_out = {}

        self.cache['next_phase'] = self._pipeline.next_phase(
            phase_out.get('jump_to_next', False)
        )

        output = {
            "output": phase_out,
            'success': self._mode == 'REMOTE' and phase_out.get('success')
        }

        if self.debug:
            self.logs['cache']['POST-COMPUTATION'] = _copy.deepcopy(self.cache)
            self.logs['output'] = {'POST-COMPUTATION': _copy.deepcopy(output)}
            self.print_logs()

        return output

    def to_stdout(self):
        """
        Deprecated.
        Support for the old library.
        """
        data = _json.loads(_sys.stdin.read())
        if data.get('cache') and len(data['cache']) > 0:
            self.cache = data['cache']
        try:
            output = self.compute(data)
            output['cache'] = self.cache

            output = _json.dumps(output)
            _sys.stdout.write(output)
        except Exception as e:
            _tb.print_exc()
            raise Exception(f"{data['state']['clientId']} error {e} ***")
