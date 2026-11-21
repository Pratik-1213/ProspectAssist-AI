"""Lead conversion probability bucketing and follow-up SLA scheduling logic."""
from typing import Mapping, Any, Literal

PriorityTier = Literal["HOT_LEAD", "WARM_OPPORTUNITY", "NURTURE_TRACK"]


def classify_lead_priority(score: float, days_since_last_contact: int = 0) -> dict[str, Any]:
    """
    Classifies a sales lead into actionable priority tiers with SLA response windows.
    - HOT_LEAD: Score >= 80 (SLA: 4 hours)
    - WARM_OPPORTUNITY: Score >= 50 (SLA: 24 hours)
    - NURTURE_TRACK: Score < 50 (SLA: 72 hours)

    Escalates SLA if a warm lead has gone uncontacted for >= 5 days.
    """
    if score < 0 or score > 100:
        raise ValueError("Lead score must be between 0 and 100")

    if score >= 80:
        tier: PriorityTier = "HOT_LEAD"
        sla_hours = 4
        action = "Direct telephone call from Senior Sales Executive"
    elif score >= 50:
        tier = "WARM_OPPORTUNITY"
        # Escalation check
        if days_since_last_contact >= 5:
            sla_hours = 12
            action = "Escalated follow-up: Send personalized demo invitation"
        else:
            sla_hours = 24
            action = "Send targeted value proposition email"
    else:
        tier = "NURTURE_TRACK"
        sla_hours = 72
        action = "Enroll in weekly educational product newsletter"

    return {
        "tier": tier,
        "score": score,
        "sla_hours": sla_hours,
        "recommended_action": action,
    }


def rank_leads_by_urgency(leads: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """
    Evaluates a collection of leads and returns them sorted by SLA hours ascending
    (most urgent response requirement first), then score descending.
    """
    evaluated = []
    for lead in leads:
        lead_id = lead.get("id", "UNKNOWN")
        score = float(lead.get("score", 0.0))
        days = int(lead.get("days_since_contact", 0))
        info = classify_lead_priority(score, days)
        info["id"] = lead_id
        evaluated.append(info)

    return sorted(evaluated, key=lambda x: (x["sla_hours"], -x["score"]))
