# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pytest
import copy

from test.fixtures.scorecard_distillation import error_tables

from metadata_generation.veritas.scorecard_distillation.scorecard_distiller import ScorecardDistiller, MetricsCalculator, TableScorecards, TableScorecard
from metadata_generation.veritas.scorecard_distillation.scorecard_distiller import DatasetScorecard, ScorecardMetrics


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * *  MetricsCalculator Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_scorecard_distiller(error_tables):
    (_, erroneous_records, missing_records) = error_tables
    scorecard_distiller = ScorecardDistiller()

    (dataset_scorecard, table_scorecards) = scorecard_distiller.distill_scorecards(erroneous_records, missing_records)


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * *  MetricsCalculator Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_set_metrics(error_tables):
    (_, erroneous_records, _) = error_tables
    table_scorecard = TableScorecard('batteryTestSummary')
    metrics_calculator = MetricsCalculator(erroneous_records)
    table_scorecard = metrics_calculator.set_metrics(table_scorecard, 'error_affected', 'erroneous')


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * *  Scorecard Tests  * * * * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_scorecard():
    table_scorecards = TableScorecards()

    table_scorecard = TableScorecard('Mock')
    table_scorecard.add_metric(1, 'erroneous')
    table_scorecard.add_metric(1, 'missing')
    table_scorecard.add_metric(1, 'error_affected')
    table_scorecard.add_metric(1, 'missing_affected')

    table_scorecards.add_scorecard('original', table_scorecard)
    table_scorecards.add_scorecard('duplicate', copy.deepcopy(table_scorecard))

    dataset_scorecard = DatasetScorecard()
    dataset_scorecard.create_composite_scorecard(table_scorecards)


#####################################################################################################################################
# * * * * * * * * * * * * * * * * * * * * * * * * * * * *   ScorecardMetrics Tests  * * * * * * * * * * * * * * * * * * * * * * * * #
#####################################################################################################################################


def test_get_accuracy():
    scorecard_metrics = ScorecardMetrics()
    scorecard_metrics.add_metric(2, 'erroneous')
    expected_result = 80

    assert scorecard_metrics.get_accuracy(10) == expected_result


def test_get_completeness():
    scorecard_metrics = ScorecardMetrics()
    scorecard_metrics.add_metric(2, 'missing')
    expected_result = 80

    assert scorecard_metrics.get_completeness(8) == expected_result


def test_get_percent_error_affected():
    scorecard_metrics = ScorecardMetrics()
    scorecard_metrics.add_metric(8, 'error_affected')
    expected_result = 80

    assert scorecard_metrics.get_percent_error_affected(10) == expected_result


def test_get_percent_erroneous():
    scorecard_metrics = ScorecardMetrics()
    scorecard_metrics.add_metric(8, 'erroneous')
    expected_result = 80

    assert scorecard_metrics.get_percent_erroneous(10) == expected_result


def test_get_percent_missing_affected():
    scorecard_metrics = ScorecardMetrics()
    scorecard_metrics.add_metric(8, 'missing_affected')
    scorecard_metrics.add_metric(2, 'missing')

    expected_result = 80

    assert scorecard_metrics.get_percent_missing_affected(8) == expected_result


def test_get_percent_missing():
    scorecard_metrics = ScorecardMetrics()
    scorecard_metrics.add_metric(4, 'missing')

    expected_result = 40

    assert scorecard_metrics.get_percent_missing(6) == expected_result


def test_combine_scorecard_metrics():
    table_scorecards = {}

    scorecard_metrics = ScorecardMetrics()
    scorecard_metrics.add_metric(1, 'erroneous')
    scorecard_metrics.add_metric(1, 'missing')
    scorecard_metrics.add_metric(1, 'error_affected')
    scorecard_metrics.add_metric(1, 'missing_affected')

    table_scorecards['original'] = scorecard_metrics
    table_scorecards['duplicate'] = copy.deepcopy(scorecard_metrics)

    table_scorecards['original'].combine_scorecard_metrics(table_scorecards['duplicate'])

    assert table_scorecards['original'].get_erroneous() == 2
    assert table_scorecards['original'].get_error_affected() == 2
    assert table_scorecards['original'].get_missing() == 2
    assert table_scorecards['original'].get_missing_affected() == 2

