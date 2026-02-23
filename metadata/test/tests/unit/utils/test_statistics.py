# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest 
import numpy as np 

from metadata_generation.utils.statistics import NormalDistribution, monotonicity_ratio


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * NormalDistribution Tests    * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'mean, std_dev, std_dev_from_mean, expected_value', 
    [(0, 1, 1, 1),
     (0, 1, -1, -1),
     (0, 1, -2, -2),
     (0, 1, 2, 2), 
     (0, 2.5, 1, 2.5),
     (0, 2.5, -1, -2.5),
     (1, 2.5, -1, -1.5),
     (1, 2.5, 1, 3.5)]
)
def test_value_x_std_dev_from_mean(mean, std_dev, std_dev_from_mean, expected_value):
    normal_distribution = NormalDistribution(mean, std_dev)
    assert normal_distribution.value_x_std_dev_from_mean(std_dev_from_mean) == expected_value


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * Monotonicity Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'sequence, expected_value', 
    [([0, 1, 2, 3], 1),
     ([0, -1, -2, -3], 1),
     ([0, 1, -1, 0, 1], 0.5), 
     ([0], 0),
     ([], 0)]
)
def test_monotonicity_ratio(sequence: list, expected_value: float) -> None:
    sequence_np = np.array(sequence)
    monotonicity = monotonicity_ratio(sequence_np)
    assert monotonicity == expected_value

