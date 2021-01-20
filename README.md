# GA-Reversi
This is a program to simulate the optimization of evaluation function on Reversi game with GA algorithm.

# Requirement
* numpy

# Installation
```bash
pip install numpy pandas
```

# Usage

### Simulates GA on reversi
```python
from GA import ga

parameter = [
    100,  # max generation
    64,   # num population
    8,    # num parents
    0.3,  # BLX alpha
    0.2,  # mutation probability
    "data_v2.json"  # The JSON file name to save
]

ga = GA(parameter)
ga.evolve()
```

# Author
* Keisuke Ueda
* University of Tokyo
