# COINSTAC computations development made easy.
#### A very intuitive wrapper for writing coinstac based computations with:

* Break down your computations in simple phases with automatic transition between phases.
* Add as many phases you want.
* Even run phases that needs to be run multiple rounds of iterations.


![PyPi version](https://img.shields.io/pypi/v/coinstac-computation)
[![YourActionName Actions Status](https://github.com/trendscenter/coinstac-computation/workflows/build/badge.svg)](https://github.com/trendscenter/coinstac-computation/actions)
![versions](https://img.shields.io/pypi/pyversions/pybadges.svg)

### Express development(see [examples](./examples/basic) folder for a simple use case):
Commands:
```
mkdir -p examples/basic/dist        --- Needed only once -------
chmod u+x deploy.sh                 --- Needed only once -------

./deploy.sh examples/basic/dist     --- Needed everytime you make some changes -------
```

### Deployment:
```
pip install coinstac-computation (or add to requirements.txt file)
```

## Example: Gather max even numbers from each site
#### A full working use case is in the [examples/basic](./examples/basic) directory where:
* Local sites filters out even numbers and sends to the remote.
* Remote finds the max across sites and returns the final result to each of the sites.
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

### Entry point:

```python
import coinstac

from local_pipeline import local
from remote_pipeline import remote

coinstac.start(local.compute, remote.compute)
```

### Run:
```
cd example
docker build -t base . && coinstac-simulator
```

<hr />

### Advanced use case: Phases with multiple iterations.
#### Overview:

1. Specify a phase as multi-iterations:
```python
local.add_phase(SomeIterativePhase, multi_iterations=True)
```

2. Specify when to end the iterative phase as:

```python
class SomeIterativePhase(ComputationPhase):
    def compute(self):
        """Do all the stuff"""
        
        """Check if the iterative phase is done, and send a phase jump signal."""
        should_jump_to_next_phase = ... 
        return {..., 'jump_to_next': should_jump_to_next_phase}
```

####  Full working [example](./examples/multi_iterations) where:
* Each sites cast a vote for multiple(default=51) times.
* Remote gathers the votes and returns the final voting result at the end.
* Sites save the final result.

<hr />
 
### Development notes:
* Make sure you have:
  * **docker** installed and running.
  * **nodejs** installed.
  * **coinstac-simulator** package installed. `npm install --global coinstac-simulator`
* Must set `debug=False` while deploying.
* Backward compatible to the older library(compspecVersion=1):
  * Add the following snippet at the end of local and remote pipeline scripts.
  ```python
  if __name__ == "__main__":
      local.to_stdout()
  ```
  * Use [version 1.0](./examples/basic/compspecv1.json) compspec format.
  * Comment out line `CMD ["python", "entry.py"]` in the `Dockerfile`.
  * You can also use a **remote debugger** in pycharm as [here](https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html#remote-debug-config).


### Thanks!
