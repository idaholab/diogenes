# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import numpy as np

from dataclasses import dataclass
from ..utils.constraints import ConstraintRange


@dataclass
class NormalDistribution:

    mean: float = 0
    std_dev: float = 0

    def value_x_std_dev_from_mean(self, std_devs_from_mean: int) -> float:
        return self.mean + (std_devs_from_mean * self.std_dev)
        
    def bounded_range_x_std_devs_from_mean(self, std_devs_from_mean: int) -> ConstraintRange:
        constraint_range = ConstraintRange()

        if std_devs_from_mean < 0:
            constraint_range.lower_bound = self.value_x_std_dev_from_mean(std_devs_from_mean - 1)
            constraint_range.upper_bound = self.value_x_std_dev_from_mean(std_devs_from_mean)
        else:
            constraint_range.lower_bound = self.value_x_std_dev_from_mean(std_devs_from_mean)
            constraint_range.upper_bound = self.value_x_std_dev_from_mean(std_devs_from_mean + 1)   

        return constraint_range

    def unbounded_range_x_std_devs_from_mean(self, std_devs_from_mean: int) -> ConstraintRange: 
        constraint_range = ConstraintRange()

        if std_devs_from_mean < 0:
            constraint_range.lower_bound = float('-inf')
            constraint_range.upper_bound = self.value_x_std_dev_from_mean(std_devs_from_mean)
        else:
            constraint_range.lower_bound = self.value_x_std_dev_from_mean(std_devs_from_mean)
            constraint_range.upper_bound = float('inf')   

        return constraint_range
    
def monotonicity_ratio(sequence: np.ndarray) -> float:
    if sequence.size == 0 or sequence.size == 1:
        return 0
    sequence_delta = np.diff(sequence)
    delta_signs = np.sign(sequence_delta)
    return abs(delta_signs.sum() / (sequence_delta.size))