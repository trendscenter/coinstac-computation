# COINSTAC computations development made easy.

![PyPi version](https://img.shields.io/pypi/v/coinstac-computation)
[![YourActionName Actions Status](https://github.com/trendscenter/coinstac-computation/workflows/build/badge.svg)](https://github.com/trendscenter/coinstac-computation/actions)
![versions](https://img.shields.io/pypi/pyversions/pybadges.svg)

### A very intuitive wrapper for writing coinstac based computations:

* Break down your computations into simple phases with automatic transition between phases.
* Add as many phases as you want.
* Phases **alternate between local and remote automatically** by default starting from the first phase of the local. See advanced use case example below for extras like:
  * Run phases that needs to be run multiple _local-remote_ trips; Specify _multi_iterations=True_ while adding a phase.
  * Run phases that needs to be run either in local or remote without making a trip(like preprocessing, gathering final results ...); Specify _local_only=True_ while adding a phase.
* Automatic logging that saves what comes and leaves on each phase. Just set `debug=True`.

#### Installation:
* Run `pip install coinstac-computation`
* Add entry `coinstac-computation` to the requirements.txt.

<hr />

<!---
### Only for this framework's express development:
Commands:
```
mkdir -p examples/basic/dist        --- Needed only once -------
chmod u+x deploy.sh                 --- Needed only once -------

./deploy.sh examples/basic/dist     --- Needed everytime you make some changes -------
```
--->

#### **ComputationPhase** signature:
```python
from coinstac_computation import  ComputationPhase

class PhaseLoadData(ComputationPhase):
    def _initialize(self):
      """Put anything that needs to be initialized only once here"""
      pass
    
    def compute(self):
        """put phase logic here"""  
        return {}
```

### Example: Gather max even numbers from each site
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

coinstac.start(local, remote)
```

### Run:
```
cd examples/basic/
~/coinstac-computation/examples/basic/$ docker build -t base . && coinstac-simulator
```

<hr />

## Advanced use case [example](./examples/multi_iterations) with multiple iterations where:

* Each sites cast a vote(positive vote if number is even) for multiple(default=51) times.
* Remote gathers the votes and returns the final voting result to all sites at the end.
* Sites save the final result.

#### Overview:

1. Specify when to end the iterative phase with a phase jump signal as `jump_to_next=True`:

```python
class PhaseSubmitVote(ComputationPhase):

    def _initialize(self):
        """This method runs only once"""
        self.cache['data_index'] = 0
        self.cache['data'] = []
        for line in open(self.state['baseDirectory'] + os.sep + self.input_args['data_source']).readlines():
            self.cache['data'].append(float(line.strip()))

    def compute(self):
        out = {
            'vote': self.cache['data'][self.cache['data_index']] % 2 == 0,
        }
        self.cache['data_index'] += 1
        
        """Send a jump to next phase signal"""
        out['jump_to_next'] = self.cache['data_index'] > len(self.cache['data']) - 1
        return out
```

2. Add the phase as multi-iterations:
```python
local.add_phase(PhaseSubmitVote, multi_iterations=True)
```

### Sample from logs file in the output directory

```
[INPUT] *** 17:03:53 [02/03/2022] ***
	-> {'data_source': 'data_file.txt'}
[CACHE] *** 17:03:53 [02/03/2022] ***
	-> {'PIPELINE:LOCAL': {'index': 0, 'iterations': {'PhaseSubmitVote': 0, 'PhaseSaveResult': 0}}}
	<- {'PIPELINE:LOCAL': {'index': 0, 'iterations': {'PhaseSubmitVote': 1, 'PhaseSaveResult': 0}}, 'input_args': {'data_source': 'data_file.txt'}, 'next_phase': 'PhaseSubmitVote', 'data_index': 1, 'data': [712.0, 309.0, 574.0, 838.0, 296.0, 349.0, 781.0, 749.0, 360.0, 702.0, 253.0, 831.0, 911.0, 14.0, 259.0, 805.0, 494.0, 501.0, 549.0, 624.0, 919.0, 836.0, 362.0, 373.0, 563.0, 134.0, 610.0, 875.0, 328.0, 299.0, 874.0, 387.0, 743.0, 233.0, 834.0, 870.0, 685.0, 342.0, 79.0, 270.0, 314.0, 42.0, 364.0, 902.0, 755.0, 248.0, 815.0, 4.0, 21.0, 423.0, 302.0], 'PHASE:PhaseSubmitVote': True}
[OUTPUT] *** 17:03:53 [02/03/2022] ***
	<- {'output': {'vote': True, 'jump_to_next': False}}


[INPUT] *** 17:03:53 [02/03/2022] ***
	-> {}
[CACHE] *** 17:03:53 [02/03/2022] ***
	-> {'PIPELINE:LOCAL': {'index': 0, 'iterations': {'PhaseSubmitVote': 1, 'PhaseSaveResult': 0}}, 'input_args': {'data_source': 'data_file.txt'}, 'next_phase': 'PhaseSubmitVote', 'data_index': 1, 'data': [712.0, 309.0, 574.0, 838.0, 296.0, 349.0, 781.0, 749.0, 360.0, 702.0, 253.0, 831.0, 911.0, 14.0, 259.0, 805.0, 494.0, 501.0, 549.0, 624.0, 919.0, 836.0, 362.0, 373.0, 563.0, 134.0, 610.0, 875.0, 328.0, 299.0, 874.0, 387.0, 743.0, 233.0, 834.0, 870.0, 685.0, 342.0, 79.0, 270.0, 314.0, 42.0, 364.0, 902.0, 755.0, 248.0, 815.0, 4.0, 21.0, 423.0, 302.0], 'PHASE:PhaseSubmitVote': True}
	<- {'PIPELINE:LOCAL': {'index': 0, 'iterations': {'PhaseSubmitVote': 2, 'PhaseSaveResult': 0}}, 'input_args': {'data_source': 'data_file.txt'}, 'next_phase': 'PhaseSubmitVote', 'data_index': 2, 'data': [712.0, 309.0, 574.0, 838.0, 296.0, 349.0, 781.0, 749.0, 360.0, 702.0, 253.0, 831.0, 911.0, 14.0, 259.0, 805.0, 494.0, 501.0, 549.0, 624.0, 919.0, 836.0, 362.0, 373.0, 563.0, 134.0, 610.0, 875.0, 328.0, 299.0, 874.0, 387.0, 743.0, 233.0, 834.0, 870.0, 685.0, 342.0, 79.0, 270.0, 314.0, 42.0, 364.0, 902.0, 755.0, 248.0, 815.0, 4.0, 21.0, 423.0, 302.0], 'PHASE:PhaseSubmitVote': True}
[OUTPUT] *** 17:03:53 [02/03/2022] ***
	<- {'output': {'vote': False, 'jump_to_next': False}}


[INPUT] *** 17:03:53 [02/03/2022] ***
	-> {}
[CACHE] *** 17:03:53 [02/03/2022] ***
	-> {'PIPELINE:LOCAL': {'index': 0, 'iterations': {'PhaseSubmitVote': 2, 'PhaseSaveResult': 0}}, 'input_args': {'data_source': 'data_file.txt'}, 'next_phase': 'PhaseSubmitVote', 'data_index': 2, 'data': [712.0, 309.0, 574.0, 838.0, 296.0, 349.0, 781.0, 749.0, 360.0, 702.0, 253.0, 831.0, 911.0, 14.0, 259.0, 805.0, 494.0, 501.0, 549.0, 624.0, 919.0, 836.0, 362.0, 373.0, 563.0, 134.0, 610.0, 875.0, 328.0, 299.0, 874.0, 387.0, 743.0, 233.0, 834.0, 870.0, 685.0, 342.0, 79.0, 270.0, 314.0, 42.0, 364.0, 902.0, 755.0, 248.0, 815.0, 4.0, 21.0, 423.0, 302.0], 'PHASE:PhaseSubmitVote': True}
	<- {'PIPELINE:LOCAL': {'index': 0, 'iterations': {'PhaseSubmitVote': 3, 'PhaseSaveResult': 0}}, 'input_args': {'data_source': 'data_file.txt'}, 'next_phase': 'PhaseSubmitVote', 'data_index': 3, 'data': [712.0, 309.0, 574.0, 838.0, 296.0, 349.0, 781.0, 749.0, 360.0, 702.0, 253.0, 831.0, 911.0, 14.0, 259.0, 805.0, 494.0, 501.0, 549.0, 624.0, 919.0, 836.0, 362.0, 373.0, 563.0, 134.0, 610.0, 875.0, 328.0, 299.0, 874.0, 387.0, 743.0, 233.0, 834.0, 870.0, 685.0, 342.0, 79.0, 270.0, 314.0, 42.0, 364.0, 902.0, 755.0, 248.0, 815.0, 4.0, 21.0, 423.0, 302.0], 'PHASE:PhaseSubmitVote': True}
[OUTPUT] *** 17:03:53 [02/03/2022] ***
	<- {'output': {'vote': True, 'jump_to_next': False}}
...
```
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
