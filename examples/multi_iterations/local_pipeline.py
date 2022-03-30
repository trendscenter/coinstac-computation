import os
import json
from coinstac_computation import COINSTACPyNode, ComputationPhase

# import pydevd_pycharm
#
# pydevd_pycharm.settrace('172.17.0.1', port=8881, stdoutToServer=True, stderrToServer=True)


class PhaseSubmitVote(ComputationPhase):

    def _initialize(self):
        self.cache['data_index'] = 0
        self.cache['data'] = []
        for line in open(self.base_dir + os.sep + self.input_args['data_source']).readlines():
            self.cache['data'].append(float(line.strip()))

    def compute(self):
        out = {
            'vote': self.cache['data'][self.cache['data_index']] % 2 == 0,
        }
        self.cache['data_index'] += 1
        out['jump_to_next'] = self.cache['data_index'] > len(self.cache['data']) - 1
        return out


class PhaseSaveResult(ComputationPhase):
    def compute(self):
        with open(f"{self.out_dir + os.sep + 'vote_results.json'}", 'w') as out:
            json.dump(self.input['vote_result'], out)


local = COINSTACPyNode(mode='local', debug=True)
local.add_phase(PhaseSubmitVote, multi_iterations=True)
local.add_phase(PhaseSaveResult)

if __name__ == "__main__":
    local.to_stdout()
