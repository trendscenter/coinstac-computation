from coinstac_computation import COINSTACPyNode, ComputationPhase, PhaseEndWithSuccess
import numpy as np


class PhaseAggregateMatrix(ComputationPhase):
    def compute(self):
        out = {}
        data = self.recv("site_matrix")
        mean_data = np.array(data).mean(0)
        out.update(**self.send("averaged_matrix", mean_data))
        return out


remote = COINSTACPyNode(mode='remote', debug=True)
remote.add_phase(PhaseAggregateMatrix)
remote.add_phase(PhaseEndWithSuccess)
