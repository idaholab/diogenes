# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import pandas as pd

from ...veritas.scorecard_distillation.scorecard_distiller import ScorecardDistiller


class ErrorCatalogReader:


    def get_scorecards(self, error_tables):
        erroneous_records = error_tables.get_erroneous_records()
        missing_records = error_tables.get_missing_records()

        scorecard_distiller = ScorecardDistiller()
        scorecards = scorecard_distiller.distill_scorecards(erroneous_records, missing_records)

        return scorecards