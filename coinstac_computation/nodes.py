import copy as _copy
import json as _json
import sys as _sys
import traceback as _tb

import coinstac_computation.utils as _utils


class COINSTACPyNode:
    _VALID_MODES_ = ['REMOTE', 'LOCAL']

    def __init__(self, mode: str, debug=False):
        self.cache = {}
        self._mode = mode.upper()
        self._pipeline = _utils.PhasePipeline(self._mode, self.cache)
        self.debug = debug
        self._logs = {}

        assert self._mode in COINSTACPyNode._VALID_MODES_, \
            f"Invalid mode : {self._mode}, Use one of: {COINSTACPyNode._VALID_MODES_}"

    def add_phase(self, phase_cls, multi_iterations=False):
        self._pipeline.add_phase(phase_cls, multi_iterations)

    def print_logs(self):
        print()
        for k, v in self._logs.items():
            print(f"[{k.upper()}]{'-' * 51}")
            for k1, v1 in v.items():
                print(f"\t[ {k1} ] -> {v1}")

    def compute(self, data):
        out = {}
        if self.debug:
            self._logs['input'] = {}
            self._logs['input']['PRE-COMPUTATION '] = _copy.deepcopy(data)
            self._logs['cache'] = {}
            self._logs['cache']['PRE-COMPUTATION '] = _copy.deepcopy(self.cache)

        if not self.cache.get('input_args'):
            """Some multi-iteration computations might need to reuse initial parameters, so save it."""
            self.cache['input_args'] = _utils.FrozenDict(_copy.deepcopy(data['input']))

        phase_key = self.cache.get('next_phase')
        if not phase_key:
            phase_key = self._pipeline.next_phase()

        phase = self._pipeline.phases[phase_key](
            phase_key,
            self.cache, data['input'], data['state']
        )

        try:
            _out = phase.compute()
            if _out:
                out.update(**_out)
        except:
            raise RuntimeError(f"ERROR! in Phase: *** {phase_key} ***")

        self.cache['next_phase'] = self._pipeline.next_phase(
            out.get('jump_to_next', False)
        )

        output = {"output": out}

        if self._mode == 'REMOTE':
            output['success'] = out.get('success', False)

        if self.debug:
            self._logs['cache']['POST-COMPUTATION'] = _copy.deepcopy(self.cache)
            self._logs['output'] = {'POST-COMPUTATION': _copy.deepcopy(output)}
            self.print_logs()

        return output

    def to_stdout(self):
        """
        Backward compatibility for the old library. Deprecated now.
        """
        data = _json.loads(_sys.stdin.read())
        if data.get('cache') and len(data['cache']) > 0:
            self.cache = data['cache']
        try:
            self.debug = False
            output = self.compute(data)
            output['cache'] = self.cache
            output = _json.dumps(output)
            _sys.stdout.write(output)
        except Exception as e:
            _tb.print_exc()
            raise Exception(f"{data['state']['clientId']} error {e} ***")
