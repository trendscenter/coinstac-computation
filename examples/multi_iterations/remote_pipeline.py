from coinstac_computation import COINSTACPyNode, ComputationPhase, PhaseEndWithSuccess, utils
import numpy as np

# import pydevd_pycharm
#
# pydevd_pycharm.settrace('172.17.0.1', port=8881, stdoutToServer=True, stderrToServer=True)


class PhaseCollectVote(ComputationPhase):
    def _initialize(self):
        self.cache['vote_ballot'] = []

    def compute(self):
        out = {}

        votes = []
        for site, site_vars in self.input.items():
            votes.append(int(site_vars['vote']))

        positives = sum(votes)
        self.cache['vote_ballot'].append([positives, len(self.input) - positives])

        sites_ready_for_next_phase = utils.check(all, 'jump_to_next', True, self.input)
        if sites_ready_for_next_phase:
            vote_data = np.array(self.cache['vote_ballot']).sum(0)
            out['vote_result'] = {
                'positive_votes': int(vote_data[0]),
                'negative_votes': int(vote_data[1])
            }
            out['jump_to_next'] = True

        return out


remote = COINSTACPyNode(mode='remote', debug=True)
remote.add_phase(PhaseCollectVote, multi_iterations=True)
remote.add_phase(PhaseEndWithSuccess)

if __name__ == "__main__":
    remote.to_stdout()
