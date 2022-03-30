import os
from coinstac_computation import COINSTACPyNode, ComputationPhase
import numpy as np


class PhaseLoadData(ComputationPhase):
    def compute(self):
        out = {}
        data = np.random.randn(*self.input['matrix_shape'])
        out.update(**self.send("site_matrix", data))
        return out


class PhaseSaveResult(ComputationPhase):
    def compute(self):
        data = self.recv('averaged_matrix')
        np.save(self.out_dir + os.sep + "averaged_matrix.npy", data)


local = COINSTACPyNode(mode='local', debug=True)
local.add_phase(PhaseLoadData)
local.add_phase(PhaseSaveResult)
