# Copyright 2026, Battelle Energy Alliance, LLC, ALL RIGHTS RESERVED

import re
import pandas as pd
import warnings
from .Agent import BaseAgent


# ---------------------------------------------------------------------------
# Column-name keyword detection
#
# Uses word-boundary matching on snake_case names so that partial hits like
# "validate" (contains "date") or "timeflag" (contains "time") are rejected.
# A keyword must appear at the start, end, or surrounded by underscores.
# ---------------------------------------------------------------------------

def _name_has_word(name: str, words) -> bool:
    """True if any word appears as a full snake_case segment in name."""
    for w in words:
        if re.search(r"(^|_)" + re.escape(w) + r"($|_)", name):
            return True
    return False


def _name_has_suffix(name: str, suffixes) -> bool:
    """True if name contains any of the literal substrings."""
    return any(s in name for s in suffixes)


_DATE_WORDS      = frozenset({"date", "datetime", "timestamp", "dt"})
_TIME_WORDS      = frozenset({"time"})
_TIME_SUFFIXES   = frozenset({"_hr", "_hour", "_min", "_minute", "_sec", "_second"})
_DURATION_WORDS  = frozenset({"duration", "dur", "elapsed", "interval"})
_ID_WORDS      = frozenset({"id", "key", "pk", "fk"})


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

# Predictions with confidence below this receive a "?" prefix in the output,
# matching the convention used by MLTree/MLTree2.
CONFIDENCE_THRESHOLD = 0.75

# unique-value / non-null ratio below which a column is considered categorical
CATEGORICAL_CUTOFF = 0.33
# hard cap for non-integer columns (strings, booleans)
MAX_UNIQUE_CATEGORIES = 500
# integers with more distinct values than this are treated as numerical regardless
# of cardinality ratio — survey codes rarely exceed ~25 unique values
MAX_INT_CATEGORIES = 25

# Fraction of sampled values that must match/parse as datetime
DATETIME_HIT_RATE = 0.85


# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

_DATE_RE = re.compile(
    r"\d{4}[-/]\d{1,2}[-/]\d{1,2}"   # YYYY-MM-DD or YYYY/MM/DD
    r"|\d{1,2}[-/]\d{1,2}[-/]\d{4}"  # DD-MM-YYYY or MM/DD/YYYY
    r"|\d{4}-\d{2}-\d{2}T"           # ISO-8601 with time component
)

_TIME_RE = re.compile(r"^\d{1,2}:\d{2}(:\d{2}(\.\d+)?)?$")


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class Tree2ProbAgent(BaseAgent):
    """
    Tree2 with probabilistic confidence weighting.

    Every internal decision carries a confidence score (0.0–1.0).  When the
    score falls below CONFIDENCE_THRESHOLD (0.75) the label is prefixed with
    "?" (e.g. "?integer", "?categorical"), matching the convention used by the
    MLTree agents.  Deterministic high-confidence cases (empty columns, name
    keyword matches, clean dtype inference) produce no "?" prefix.

    Confidence sources
    ------------------
    Type:
      (none) / (redacted)                → 1.00  (unambiguous)
      name keyword match                  → 0.85  (strong hint but data not verified)
      boolean dtype                       → 0.95
      Int64 dtype                         → 0.92
      Float64 where all values are
        whole numbers (integer-coded)     → 0.78
      Float64 (true float)                → 0.88
      string dtype — boolean strings      → 0.90
      string dtype — json / xml           → 0.85
      string dtype — datetime             → proportional to parse hit-rate (0.70–0.95)
      string dtype — time pattern         → 0.85
      string dtype — fallback string      → 0.82
      object dtype fallback               → above × 0.80
      no match                            → 0.00

    Class:
      fixed type mappings                 → 0.95
      primary key (100 % unique)          → 0.90
      sequential integer                  → 0.85
      foreign key by name                 → 0.80
      categorical: scales with distance
        from CATEGORICAL_CUTOFF
        (low ratio → high; borderline → low → "?categorical")
      numerical                           → 0.82
      string / boolean fallback           → 0.80
    """

    def __init__(self):
        pass

    def guess(self, row_name: str, data: pd.Series):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            type_val,  type_conf  = self._guess_type(row_name, data)
            class_val, class_conf = self._guess_class(row_name, data, type_val)

        # Apply "?" prefix for low-confidence predictions, matching MLTree convention.
        _no_prefix_types   = {"?", "(none)", "(redacted)"}
        _no_prefix_classes = {"?", "none"}

        if type_conf < CONFIDENCE_THRESHOLD and type_val not in _no_prefix_types:
            type_val = "?" + type_val
        if class_conf < CONFIDENCE_THRESHOLD and class_val not in _no_prefix_classes:
            class_val = "?" + class_val

        return type_val, class_val

    # ------------------------------------------------------------------
    # Type detection  (returns (label, confidence))
    # ------------------------------------------------------------------

    def _guess_type(self, row_name: str, data: pd.Series):
        non_null = data.dropna()

        if len(non_null) == 0:
            return "(none)", 1.0

        if self._is_explicitly_redacted(non_null):
            return "(redacted)", 1.0

        name = row_name.lower()
        if _name_has_word(name, _DATE_WORDS):
            return "date-time", 0.85
        if not _name_has_word(name, _DURATION_WORDS):
            if _name_has_word(name, _TIME_WORDS) or _name_has_suffix(name, _TIME_SUFFIXES):
                return "time", 0.85

        inferred_dtype = str(non_null.convert_dtypes().dtype)

        if inferred_dtype == "boolean":
            return "boolean", 0.95

        if inferred_dtype == "Int64":
            return "integer", 0.92

        if inferred_dtype == "Float64":
            numeric = pd.to_numeric(non_null, errors="coerce").dropna()
            if len(numeric) > 0 and (numeric % 1 == 0).all():
                return "integer", 0.78   # whole-number float → probably integer-coded
            return "float", 0.88

        if inferred_dtype == "string":
            return self._classify_string_series(non_null)

        if inferred_dtype == "object":
            label, conf = self._classify_string_series(non_null.astype(str))
            return label, conf * 0.80   # object dtype is inherently less certain

        return "?", 0.0

    def _classify_string_series(self, non_null: pd.Series):
        """Return (type_label, confidence) for a string-valued Series."""
        stripped = non_null.str.strip()

        unique_lower = set(stripped.str.lower().dropna().unique())
        if unique_lower and unique_lower.issubset({"true", "false", "yes", "no", "1", "0"}):
            return "boolean", 0.90

        sample = stripped.dropna().head(300)

        if len(sample) > 0:
            starts_curly   = sample.str.startswith("{").mean()
            starts_bracket = sample.str.startswith("[").mean()
            starts_angle   = sample.str.startswith("<").mean()
            if starts_curly > 0.8 or starts_bracket > 0.8:
                return "json", 0.85
            if starts_angle > 0.8:
                return "xml", 0.85

        hit_rate = self._datetime_hit_rate(sample)
        if hit_rate >= DATETIME_HIT_RATE:
            has_time = sample.str.contains(r"\d{2}:\d{2}", regex=True, na=False).any()
            label = "date-time" if has_time else "date"
            # Confidence proportional to how cleanly the values parsed
            return label, 0.70 + hit_rate * 0.25

        if self._time_hit_rate(sample) >= DATETIME_HIT_RATE:
            return "time", 0.85

        return "string", 0.82

    def _datetime_hit_rate(self, sample: pd.Series) -> float:
        """Fraction of sample values that successfully parse as datetime (0.0–1.0)."""
        if len(sample) == 0:
            return 0.0
        if pd.to_numeric(sample, errors="coerce").notna().mean() > 0.9:
            return 0.0   # purely numeric → not dates
        if sample.str.contains(_DATE_RE, regex=True, na=False).mean() < DATETIME_HIT_RATE:
            return 0.0
        parsed = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
        return float(parsed.notna().mean())

    def _time_hit_rate(self, sample: pd.Series) -> float:
        if len(sample) == 0:
            return 0.0
        return float(sample.str.match(_TIME_RE, na=False).mean())

    # ------------------------------------------------------------------
    # Class detection  (returns (label, confidence))
    # ------------------------------------------------------------------

    def _guess_class(self, row_name: str, data: pd.Series, data_type: str):
        if data_type in ("(redacted)", "(none)"):
            return "none", 0.95
        if data_type == "time":
            return "numerical", 0.95
        if data_type == "date":
            return "date", 0.95
        if data_type == "date-time":
            return "date", 0.95
        if data_type in ("json", "xml", "blob"):
            return "none", 0.95

        non_null = data.dropna()
        if len(non_null) == 0:
            return "none", 0.95

        name = row_name.lower()
        is_id_col = (
            name == "id"
            or name.endswith("id")
            or _name_has_word(name, _ID_WORDS)
        )

        if self._is_primary_key(non_null, data):
            if is_id_col and ("fk" in name or "foreign" in name):
                return "foreign_key", 0.80
            return "primary_key", 0.90

        if is_id_col and data_type in ("integer", "float", "string"):
            return "foreign_key", 0.80

        if data_type == "integer" and self._is_sequential(non_null):
            return "sequence", 0.85

        cat_conf = self._categorical_confidence(non_null, data_type)
        if cat_conf is not None and data_type != "float":
            return "categorical", cat_conf

        if data_type in ("integer", "float"):
            return "numerical", 0.82

        if data_type in ("string", "boolean"):
            return "categorical", 0.80

        return "?", 0.0

    # ------------------------------------------------------------------
    # Helper predicates
    # ------------------------------------------------------------------

    @staticmethod
    def _is_explicitly_redacted(non_null: pd.Series) -> bool:
        if len(non_null) == 1 and "redact" in str(non_null.iloc[0]).lower():
            return True
        try:
            if non_null.astype(str).str.lower().str.contains("redact", na=False).all():
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def _is_primary_key(non_null: pd.Series, data: pd.Series) -> bool:
        if len(non_null) < len(data) * 0.95:
            return False
        return non_null.nunique() == len(non_null)

    @staticmethod
    def _is_sequential(non_null: pd.Series) -> bool:
        try:
            numeric = pd.to_numeric(non_null, errors="coerce").dropna().sort_values()
            if len(numeric) < 3:
                return False
            diffs = numeric.diff().dropna()
            return bool((diffs > 0).all() and diffs.nunique() == 1)
        except Exception:
            return False

    @staticmethod
    def _categorical_confidence(non_null: pd.Series, data_type: str = "string"):
        """
        Return a confidence score if the column qualifies as categorical, else None.

        Integers use a stricter unique-value cap (MAX_INT_CATEGORIES = 25) because
        integer columns with many distinct values are almost always numerical codes,
        not categorical labels.  Strings and booleans use the larger cap (500).

        Confidence scales with how far the cardinality ratio is below the cutoff:
          ratio ≈ 0.00 → ~0.95  (obviously categorical)
          ratio ≈ 0.20 → ~0.74  (borderline → "?categorical")
          ratio = 0.33 → ~0.60  (at the cutoff edge → "?categorical")
        """
        n_unique = non_null.nunique()
        n_total  = len(non_null)
        if n_total == 0:
            return None
        ratio = n_unique / n_total
        max_cats = MAX_INT_CATEGORIES if data_type == "integer" else MAX_UNIQUE_CATEGORIES
        if n_unique > max_cats or ratio > CATEGORICAL_CUTOFF:
            return None
        # Linear scale: 0.95 at ratio=0, 0.60 at ratio=CATEGORICAL_CUTOFF
        return 0.95 - (ratio / CATEGORICAL_CUTOFF) * 0.35
