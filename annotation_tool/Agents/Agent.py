# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

class BaseAgent:
    """
    This is a placeholder Agent.
    It will not guess any annotations.
    """

    def __init__(self):
        pass

    def guess(self, row_name, data):
        return "?", "?"
