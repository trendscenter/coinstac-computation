from coinstac_computation import COINSTACPyNode, ComputationPhase
import os


class PhaseLoadData(ComputationPhase):
    def compute(self):
        data = []
        for d in self.input['data']:
            if d % 2 == 0:
                data.append(d)
        return {'filtered_data': data}


class PhaseSaveResult(ComputationPhase):
    def compute(self):
        with open(f"{self.state['outputDirectory'] + os.sep + 'results.txt'}", 'w') as out:
            out.write(f"{self.input['aggregated_data']}")
        return {'success': True}


local = COINSTACPyNode(mode='local', debug=True)
local.add_phase(PhaseLoadData)
local.add_phase(PhaseSaveResult)

if __name__ == "__main__":
    local.to_stdout()
