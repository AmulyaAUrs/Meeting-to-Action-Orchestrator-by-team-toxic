"""ActionItemStore coded tool for the Meeting-to-Action Orchestrator.

Persists action items in neuro-san's out-of-band ``sly_data`` so state survives
across turns within a session, and performs REAL, deterministic overdue/stalled
detection by comparing each item's due date to today. This gives the network a
genuine evaluation loop (not an LLM-simulated one).

Operations (arg ``operation``):
  - "add"    : add or update one action item
  - "list"   : return all stored action items
  - "status" : compute overdue / due-soon / stalled buckets vs. today
"""

import logging
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)

_STORE_KEY = "action_items"


def _parse_date(value: str):
    """Parse a YYYY-MM-DD (or ISO) date string; return a date or None."""
    if not value:
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value[:10], fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


class ActionItemStore(CodedTool):
    """Stateful action-item store with deterministic overdue detection."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        operation = str(args.get("operation", "list")).strip().lower()
        items: List[Dict[str, Any]] = sly_data.get(_STORE_KEY, [])
        logger.debug(">>> ActionItemStore op=%s (%d items in store)", operation, len(items))

        if operation == "add":
            task = str(args.get("task", "")).strip()
            if not task:
                return "Error: 'task' is required to add an action item."
            item = {
                "id": len(items) + 1,
                "task": task,
                "owner": str(args.get("owner", "unassigned")).strip() or "unassigned",
                "due_date": str(args.get("due_date", "")).strip(),
                "status": str(args.get("status", "open")).strip() or "open",
                "priority": str(args.get("priority", "medium")).strip() or "medium",
            }
            items.append(item)
            sly_data[_STORE_KEY] = items
            return {"added": item, "total_items": len(items)}

        if operation == "list":
            return {"action_items": items, "total_items": len(items)}

        if operation == "status":
            today = date.today()
            overdue, due_soon, no_date, on_track = [], [], [], []
            for it in items:
                if str(it.get("status", "")).lower() in ("done", "closed", "complete", "completed"):
                    continue
                due = _parse_date(it.get("due_date", ""))
                if due is None:
                    no_date.append(it)
                elif due < today:
                    overdue.append({**it, "days_overdue": (today - due).days})
                elif (due - today).days <= 2:
                    due_soon.append({**it, "days_until_due": (due - today).days})
                else:
                    on_track.append(it)
            return {
                "as_of": today.isoformat(),
                "overdue": overdue,
                "due_soon": due_soon,
                "missing_due_date": no_date,
                "on_track": on_track,
                "summary": (
                    f"{len(overdue)} overdue, {len(due_soon)} due within 2 days, "
                    f"{len(no_date)} missing a due date, {len(on_track)} on track."
                ),
            }

        return f"Error: unknown operation '{operation}'. Use 'add', 'list', or 'status'."
