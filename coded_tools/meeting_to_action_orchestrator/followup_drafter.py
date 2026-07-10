"""FollowUpDrafter coded tool for the Meeting-to-Action Orchestrator.

Deterministically generates ready-to-send follow-up communications (per-owner
task emails and simple calendar invite stubs) from the action items stored in
``sly_data``. This grounds the CalendarComms agent in the actual tracked tasks.
"""

import logging
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)

_STORE_KEY = "action_items"


class FollowUpDrafter(CodedTool):
    """Builds per-owner follow-up emails and calendar invite stubs."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        items = sly_data.get(_STORE_KEY, [])
        meeting_title = str(args.get("meeting_title", "Team Meeting")).strip() or "Team Meeting"
        logger.debug(">>> FollowUpDrafter over %d items for '%s'", len(items), meeting_title)

        if not items:
            return {"note": "No action items stored yet. Add items before drafting follow-ups."}

        by_owner = defaultdict(list)
        for it in items:
            if str(it.get("status", "")).lower() in ("done", "closed", "complete", "completed"):
                continue
            by_owner[str(it.get("owner", "unassigned")).strip() or "unassigned"].append(it)

        emails = []
        invites = []
        for owner, owner_items in by_owner.items():
            lines = [f"Hi {owner},", "",
                     f"Following up on action items from '{meeting_title}':", ""]
            for it in owner_items:
                due = it.get("due_date") or "no due date"
                lines.append(f"  - [{it.get('priority', 'medium').upper()}] {it['task']} (due {due})")
            lines += ["", "Please confirm you're on track. Thanks!"]
            emails.append({
                "to": owner,
                "subject": f"Action items from {meeting_title}",
                "body": "\n".join(lines),
            })
            # One consolidated check-in invite per owner with any due date.
            due_dates = [it.get("due_date") for it in owner_items if it.get("due_date")]
            if due_dates:
                invites.append({
                    "attendee": owner,
                    "title": f"Check-in: {meeting_title} action items",
                    "suggested_before": min(due_dates),
                    "agenda": f"Review {len(owner_items)} open action item(s).",
                })

        return {
            "follow_up_emails": emails,
            "calendar_invites": invites,
            "count": {"emails": len(emails), "invites": len(invites)},
        }
