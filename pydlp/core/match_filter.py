"""Dynamic metadata matching and filtering engine for Py-dlp.

Supports complex boolean conditions like:
--match-filter "duration > 60 & view_count >= 1000 & !is_live"
--min-filesize 10M --max-filesize 500M
--dateafter 20260101 --datebefore 20260901
"""

from __future__ import annotations

import ast
import operator
import re
from typing import Any, Callable, Dict, Optional

from pydlp.core.ratelimit import parse_rate_limit
from pydlp.core.types import MediaInfo


class MatchFilter:
    """Evaluates whether MediaInfo satisfies configured matching criteria."""

    def __init__(
        self,
        match_filter_str: Optional[str] = None,
        min_filesize: Optional[str | int] = None,
        max_filesize: Optional[str | int] = None,
        dateafter: Optional[str] = None,
        datebefore: Optional[str] = None,
    ):
        self.match_filter_str = match_filter_str
        self.min_filesize = parse_rate_limit(min_filesize) if min_filesize else None
        self.max_filesize = parse_rate_limit(max_filesize) if max_filesize else None
        self.dateafter = str(dateafter).strip() if dateafter else None
        self.datebefore = str(datebefore).strip() if datebefore else None

    @property
    def is_active(self) -> bool:
        return bool(
            self.match_filter_str
            or self.min_filesize
            or self.max_filesize
            or self.dateafter
            or self.datebefore
        )

    def matches(self, info: MediaInfo) -> Tuple[bool, Optional[str]]:
        """Returns (passes_filter: bool, reason_if_rejected: str)."""
        if not self.is_active:
            return True, None

        # 1. Date Filter Checks (YYYYMMDD)
        if self.dateafter and info.upload_date:
            if info.upload_date < self.dateafter:
                return False, f"Upload date {info.upload_date} is before dateafter threshold {self.dateafter}"

        if self.datebefore and info.upload_date:
            if info.upload_date > self.datebefore:
                return False, f"Upload date {info.upload_date} is after datebefore threshold {self.datebefore}"

        # 2. Filesize Filter Checks
        if info.formats:
            approx_size = max([f.filesize or 0 for f in info.formats] or [0])
            if self.min_filesize and approx_size > 0 and approx_size < self.min_filesize:
                return False, f"Estimated filesize {approx_size} B is less than min-filesize {self.min_filesize} B"
            if self.max_filesize and approx_size > 0 and approx_size > self.max_filesize:
                return False, f"Estimated filesize {approx_size} B exceeds max-filesize {self.max_filesize} B"

        # 3. Dynamic Expression Filter
        if self.match_filter_str:
            passes = self._evaluate_expression(self.match_filter_str, info)
            if not passes:
                return False, f"Video did not match filter expression: '{self.match_filter_str}'"

        return True, None

    def _evaluate_expression(self, expr: str, info: MediaInfo) -> bool:
        """Safely evaluates a boolean condition string against MediaInfo attributes."""
        info_dict = info.to_dict()

        # Support 'duration > 60 & view_count >= 1000' or 'duration > 60 and view_count >= 1000'
        # Normalize '&' to ' and ', '|' to ' or ', '!' to ' not '
        normalized = expr
        normalized = re.sub(r"\s*&\s*", " and ", normalized)
        normalized = re.sub(r"\s*\|\s*", " or ", normalized)
        normalized = re.sub(r"!(?!=)", " not ", normalized)

        # Parse simple comparisons: var op val
        # Examples: "duration > 60", "view_count >= 1000", "is_live == false"
        clauses = [c.strip() for c in re.split(r"\s+and\s+", normalized, flags=re.IGNORECASE) if c.strip()]

        for clause in clauses:
            if not self._eval_single_clause(clause, info_dict):
                return False

        return True

    def _eval_single_clause(self, clause: str, context: Dict[str, Any]) -> bool:
        # Match pattern: var operator value
        m = re.match(r"^([a-zA-Z0-9_]+)\s*(<=|>=|!=|==|<|>|=)\s*(.+)$", clause)
        if not m:
            # Check for simple boolean flag existence like '!is_live' or 'is_live'
            if clause.startswith("not "):
                var = clause[4:].strip()
                return not bool(context.get(var))
            return bool(context.get(clause))

        var_name, op, val_str = m.groups()
        val_str = val_str.strip().strip("'\"")

        actual_val = context.get(var_name)
        if actual_val is None:
            return False

        # Cast types
        try:
            if isinstance(actual_val, (int, float)):
                target_val = float(val_str)
                actual_num = float(actual_val)
                if op in ("==", "="):
                    return actual_num == target_val
                elif op == "!=":
                    return actual_num != target_val
                elif op == "<":
                    return actual_num < target_val
                elif op == "<=":
                    return actual_num <= target_val
                elif op == ">":
                    return actual_num > target_val
                elif op == ">=":
                    return actual_num >= target_val
            elif isinstance(actual_val, bool):
                target_bool = val_str.lower() in ("true", "1", "yes")
                if op in ("==", "="):
                    return actual_val is target_bool
                elif op == "!=":
                    return actual_val is not target_bool
            else:
                # String comparison
                actual_str = str(actual_val)
                if op in ("==", "="):
                    return actual_str == val_str
                elif op == "!=":
                    return actual_str != val_str
        except Exception:
            return False

        return True
