# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest

from metadata_generation.veritas.scorecard_distillation.scorecard_distiller import RecordSpecificErrorTracker, MultiErrorAffectedRecord


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * MultiErrorAffectedRecord Tests  * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


@pytest.mark.parametrize(
    'initial_error_probability, subsequent_error_probabilities, expected_record_probability',
     [(0.3, [0.5], 1.0),
      (0.1, [0.1, 0.1], 1.0),
      (0.1, [0.1], 0.2),
      (0.8, [], 0.8)]
)
def test_multi_error_affected_records_single_probability(initial_error_probability, subsequent_error_probabilities, expected_record_probability):
    multi_error_affected_record = MultiErrorAffectedRecord(initial_error_probability)
    for probability in subsequent_error_probabilities:
        multi_error_affected_record.factor_in_additional_probability(probability)
    records_probability = multi_error_affected_record.get_probability()
    assert records_probability == expected_record_probability


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * RecordSpecificErrorTracker Tests  * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################

@pytest.mark.parametrize(
    'error_probabilities, expected_affected_record_increments, expected_actual_record_increments',
     [([0.3, 0.5], [1,0], [0.3, 0.7]),
      ([0.1, 0.1, 0.1, 0.1], [1,0,0,0], [0.1, 0.1, 0.8, 0]),
      ([0.1, 0.1], [1,0], [0.1, 0.1]),
      ([0.8], [1], [0.8])]
)
def test_record_specific_error_tracker_single_index(error_probabilities, expected_affected_record_increments, expected_actual_record_increments):
    different_records_in_test = 3
    record_specific_error_tracker = RecordSpecificErrorTracker()
    for record_index in range(different_records_in_test):
        for data_index, probability in enumerate(error_probabilities):
            record = {'error_probability' : probability}
            affected_increment, actual_increment = record_specific_error_tracker.get_increments_based_on_seen(record_index, record)
            assert affected_increment == expected_affected_record_increments[data_index]
            assert actual_increment == expected_actual_record_increments[data_index]
