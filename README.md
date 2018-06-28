## Gym env for the SPL-T game

Wrapper around a simulation of SPL-T, to fit it into the `gym` reinforcement learning framework.

### Installation
```
git clone https://github.com/KPLauritzen/gym-splt
cd gym-splt
pip install -e .
```

### Usage
To initialize the env:
```
import gym
import gym_splt
env = gym.make('splt-v0')
```

See [gym docs]( https://github.com/openai/gym ) for further instruction in how to interact with a `gym.Env`. 


### Credits
Inspired by the game [SPL-T](http://simogo.com/work/spl-t/) by SIMOGO. 

The core simulation was done by Craig Polley in [brute_spl-t](https://gitlab.com/flashingLEDs/brute_spl-t).