# COINSTAC computations development made easy.

### Express development(see example folder for a use case):
```
1. mkdir -p dist
2. chmod u+x deploy.sh
3. ./deploy.sh <path to dist folder>
```
Where `<path to dist folder>` is a dir in your computation that Dockerfile picks and installs in the container by:

```
RUN pip install "/computation/dist/$(ls -t1 dist|  head -n 1)"
```

### Deployment:
```
pip install coinstac-computation
```

#### Coinstac base computation framework that supports:

* Multiple computation phases.
* Multiple iterations per phase.
* Automatic phase transition.

## Use case: Gather max even numbers from each site
#### A full working use case is in the example directory where
* Local sites filters out even number and send to remote.
* Remote Finds the max for each site and returns to all sites.
* Sites save final result.

#### inputspec.json data:
```json
[
  {
    "data": {
      "value": [10, 3, 5, 6, 7, 8, 12, 38, 32, 789, 776, 441]
    }
  },
  {
    "data": {
      "value": [12, 33, 88, 61, 37, 58, 103, 3386, 312, 9, 77, 41]
    }
  }
]
```

### Local node pipeline:

```python
import os
from coinstac_computation import COINSTACPyNode, ComputationPhase


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

```

### Remote node pipeline:

```python
from coinstac_computation import COINSTACPyNode, ComputationPhase, PhaseEndWithSuccess


class PhaseCollectMaxEvenData(ComputationPhase):
    def compute(self):
        data = []
        for site, site_vars in self.input.items():
            site_max = max(site_vars['filtered_data'])
            data.append(site_max)
        return {'aggregated_data': data}


remote = COINSTACPyNode(mode='remote', debug=True)
remote.add_phase(PhaseCollectMaxEvenData)
remote.add_phase(PhaseEndWithSuccess)
```

### Entry point

```python
import coinstac

from local_pipeline import local
from remote_pipeline import remote

coinstac.start(local.compute, remote.compute)
```
<hr />

### Run
```
cd example
docker build -t base . && coinstac-simulator
```

#### Extras:
* Must set `debug=False` while deploying.
* Is backward compaitible to compspecVersion=1(deprecated now):
  * Add the following snippet at the end of local and remote pipeline scripts.
  * Use compspecVersion1 format.
```python
if __name__ == "__main__":
    local_node.to_stdout()

```
#### Specify a phase that needs to be run multiple inerations as:
```python
remote.add_phase(SomeIterativePhase, multi_iterations=True)
```
and to stop, just return jump_to_next=True as:
```python
class SomeIterativePhase(ComputationPhase):
    def compute(self):
        """All your stuff here..."""
        
        """check if you are done with this phase 
            and want to jump to the next.
        """
        should_jump:bool = ... 
        return {..., 'jump_to_next':should_jump}
```
