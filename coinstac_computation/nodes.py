import copy as _copy
import json as _json
import os
import sys as _sys

import coinstac_computation.utils as _ut
import datetime as _dt
import multiprocessing as _mp


class COINSTACPyNode:
    _VALID_MODES_ = [_ut.MODE_LOCAL, _ut.MODE_REMOTE]

    def __init__(self, mode: str, debug=False):
        self.cache = {}
        self.input = None
        self.state = None

        self.mode = mode.upper()
        self.debug = debug

        self._logs = {}
        self._pipeline_ = _ut.PhasePipeline(self.mode, self.cache)
        self.pool = None

        assert self.mode in COINSTACPyNode._VALID_MODES_, \
            f"Invalid mode : {self.mode}, Use one of: {COINSTACPyNode._VALID_MODES_}"

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
        self._pipeline_.add_phase(phase_cls, local_only, multi_iterations)

    def _save_logs(self, state):
        date_time = _dt.datetime.now().strftime("%H:%M:%S %m/%d/%Y")

        with open(
                state['outputDirectory'] + os.sep + f"{self.mode}_{state['clientId']}_logs.txt", 'a'
        ) as log:
            for k, v in self._logs.items():
                print(f"[{k.upper()}] {date_time} ", file=log)
                for k1, v1 in v.items():
                    print(f"  {k1}{v1}", file=log)
            print('', file=log)

    def _initialize(self):
        self.cache['input_args'] = _ut.FrozenDict(_copy.deepcopy(self.input))
        self.pool = _mp.Pool(self.cache.setdefault('num_workers', 2))

    def compute(self, data):
        self.input = data['input']
        self.state = data['state']

        if not self.cache.get(self.mode):
            self._initialize()
            self.cache[self.mode] = True

        if self.debug:
            self._logs['input'] = {}
            self._logs['input']['->'] = _copy.deepcopy(self.input)
            self._logs['cache'] = {}
            self._logs['cache']['->'] = _copy.deepcopy(self.cache)

        phase_key = self.cache.setdefault('next_phase', self._pipeline_.phase_ids[0])
        if self.mode == _ut.MODE_LOCAL and self.input.get('jump_to_next'):
            phase_key = self._pipeline_.next_phase(self.input['jump_to_next'])

        phase_out = self._pipeline_.phases[phase_key](phase_key, self).compute()
        if not isinstance(phase_out, dict):
            phase_out = {}

        node_output = {"output": phase_out}

        jump_to_next = phase_out.get('jump_to_next', False)
        if self.mode == _ut.MODE_REMOTE:
            jump_to_next = jump_to_next or _ut.check(all, 'jump_to_next', True, self.input)
            node_output['success'] = phase_out.get('success', False)

        self.cache['next_phase'] = self._pipeline_.next_phase(jump_to_next)

        if self._pipeline_.local_only.get(self.cache['next_phase']):
            node_output = self.compute(data)

        if self.debug:
            self._logs['cache']['<-'] = _copy.deepcopy(self.cache)
            self._logs['output'] = {'<-': _copy.deepcopy(node_output)}
            self._save_logs(self.state)

        return node_output

    def __call__(self, *args, **kwargs):
        return self.compute(*args, **kwargs)

    def to_stdout(self):
        """
        Backward compatibility for the old library. Deprecated now.
        """
        data = _json.loads(_sys.stdin.read())
        if data.get('cache') and len(data['cache']) > 0:
            self.cache = data['cache']
            self._pipeline_.cache = self.cache

        output = self.compute(data)
        output['cache'] = self.cache

        _sys.stdout.write(_json.dumps(output))
