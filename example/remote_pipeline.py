from coinstac_computation import COINSTACPyNode, ComputationPhase


class PhaseCollectMaxEvenData(ComputationPhase):
    def compute(self):
        data = []
        for site, site_vars in self.input.items():
            site_max = max(site_vars['filtered_data'])
            data.append(site_max)
        return {'aggregated_data': data}


class PhaseEnd(ComputationPhase):
    def compute(self):
        return {'success': True}


remote = COINSTACPyNode(mode='remote', debug=True)
remote.add_phase(PhaseCollectMaxEvenData)
remote.add_phase(PhaseEnd)

if __name__ == "__main__":
    remote.to_stdout()
