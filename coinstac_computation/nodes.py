import copy as _copy
import json as _json
import os
import sys as _sys

import coinstac_computation.utils as _ut
import datetime as _dt


class COINSTACPyNode:
    _VALID_MODES_ = ['REMOTE', 'LOCAL']

    def __init__(self, mode: str, debug=False):
        self._cache = {}
        self._mode = mode.upper()
        self._logs = {}
        self._debug = debug
        self._pipeline = _ut.PhasePipeline(self._mode, self._cache)

        assert self._mode in COINSTACPyNode._VALID_MODES_, \
            f"Invalid mode : {self._mode}, Use one of: {COINSTACPyNode._VALID_MODES_}"

    def add_phase(self, phase_cls, local_only: bool = False, multi_iterations: bool = False):
        """
        :param phase_cls: Custom implementation of ComputationPhase class
        :type phase_cls: ComputationPhase
        :param local_only: This phase will run only locally right after the previous phase is done.
        :type local_only: bool
        :param multi_iterations: Specifies if it is a multiple iterations phase.
        :type multi_iterations: bool
        Note: It is assumed that a normal(default) computation phase will run one round of local-remote.
        """
        self._pipeline.add_phase(phase_cls, local_only, multi_iterations)

    def _save_logs(self, state):
        date_time = _dt.datetime.now().strftime("%H:%M:%S %m/%d/%Y")

        with open(
                state['outputDirectory'] + os.sep + f"{self._mode}_{state['clientId']}_logs.txt", 'a'
        ) as log:
            for k, v in self._logs.items():
                print(f"[{k.upper()}] {date_time} ", file=log)
                for k1, v1 in v.items():
                    print(f"  {k1}{v1}", file=log)
            print('', file=log)

    def compute(self, data):
        out = {}
        if self._debug:
            self._logs['input'] = {}
            self._logs['input']['->'] = _copy.deepcopy(data['input'])
            self._logs['cache'] = {}
            self._logs['cache']['->'] = _copy.deepcopy(self._cache)

        if not self._cache.get('input_args'):
            """Some multi-iteration computations might need to reuse initial parameters, so save it."""
            self._cache['input_args'] = _ut.FrozenDict(_copy.deepcopy(data['input']))

        phase_key = self._cache.setdefault('next_phase', self._pipeline.phase_ids[0])
        if self._mode == "LOCAL" and data['input'].get('jump_to_next'):
            phase_key = self._pipeline.next_phase(data['input']['jump_to_next'])

        phase = self._pipeline.phases[phase_key](
            phase_key,
            self._cache, data['input'], data['state']
        )

        _out = phase.compute()
        if _out:
            out.update(**_out)

        output = {"output": out}

        jump_to_next = out.get('jump_to_next', False)
        if self._mode == 'REMOTE':
            jump_to_next = jump_to_next or _ut.check(all, 'jump_to_next', True, data['input'])
            output['success'] = out.get('success', False)

        self._cache['next_phase'] = self._pipeline.next_phase(jump_to_next)

        if self._pipeline.local_only.get(self._cache['next_phase']):
            output = self.compute(data)

        if self._debug:
            self._logs['cache']['<-'] = _copy.deepcopy(self._cache)
            self._logs['output'] = {'<-': _copy.deepcopy(output)}
            self._save_logs(data['state'])

        return output

    def __call__(self, *args, **kwargs):
        return self.compute(*args, **kwargs)

    def to_stdout(self):
        """
        Backward compatibility for the old library. Deprecated now.
        """
        data = _json.loads(_sys.stdin.read())
        if data.get('cache') and len(data['cache']) > 0:
            self._cache = data['cache']
            self._pipeline.cache = self._cache

        output = self.compute(data)
        output['cache'] = self._cache

        _sys.stdout.write(_json.dumps(output))
