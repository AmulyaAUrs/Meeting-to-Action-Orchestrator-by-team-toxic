"""WorkloadAnalyzer coded tool for the Meeting-to-Action Orchestrator.

Deterministically analyzes the action items stored in ``sly_data`` to detect
overcommitted owners. This grounds the PriorityPlanner's capacity warnings in
real counts rather than LLM guesswork.
"""

import logging
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)

_STORE_KEY = "action_items"

# An owner with more than this many open items is flagged as overcommitted.
_OVERLOAD_THRESHOLD = 3
# High-priority open items above this count is also a red flag.
_HIGH_PRIORITY_THRESHOLD = 2


class WorkloadAnalyzer(CodedTool):
    """Counts open tasks per owner and flags overcommitment."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        items = sly_data.get(_STORE_KEY, [])
        logger.debug(">>> WorkloadAnalyzer over %d items", len(items))

        if not items:
            return {"note": "No action items stored yet. Add items before analyzing workload."}

        per_owner_total = defaultdict(int)
        per_owner_high = defaultdict(int)
        for it in items:
            if str(it.get("status", "")).lower() in ("done", "closed", "complete", "completed"):
                continue
            owner = str(it.get("owner", "unassigned")).strip() or "unassigned"
            per_owner_total[owner] += 1
            if str(it.get("priority", "")).lower() == "high":
                per_owner_high[owner] += 1

        distribution = []
        overcommitted = []
        for owner, total in sorted(per_owner_total.items(), key=lambda kv: kv[1], reverse=True):
            high = per_owner_high.get(owner, 0)
            entry = {"owner": owner, "open_tasks": total, "high_priority": high}
            distribution.append(entry)
            if total > _OVERLOAD_THRESHOLD or high > _HIGH_PRIORITY_THRESHOLD:
                overcommitted.append(
                    {**entry, "reason": (
                        f"{total} open tasks" + (f", {high} high-priority" if high else "")
                    )}
                )

        return {
            "workload_distribution": distribution,
            "overcommitted_owners": overcommitted,
            "recommendation": (
                "Redistribute or reprioritize tasks for the overcommitted owners above."
                if overcommitted else "Workload is balanced across owners."
            ),
        }
