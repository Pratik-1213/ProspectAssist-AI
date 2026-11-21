import pytest
from lead_scheduler import classify_lead_priority, rank_leads_by_urgency


def test_classify_hot_lead():
    res = classify_lead_priority(85.0)
    assert res["tier"] == "HOT_LEAD"
    assert res["sla_hours"] == 4
    assert "telephone call" in res["recommended_action"]


def test_classify_warm_lead_standard():
    res = classify_lead_priority(65.0, days_since_last_contact=2)
    assert res["tier"] == "WARM_OPPORTUNITY"
    assert res["sla_hours"] == 24


def test_classify_warm_lead_escalation():
    # Warm lead with 6 days without contact escalates SLA from 24h to 12h
    res = classify_lead_priority(65.0, days_since_last_contact=6)
    assert res["tier"] == "WARM_OPPORTUNITY"
    assert res["sla_hours"] == 12
    assert "Escalated" in res["recommended_action"]


def test_classify_nurture_lead():
    res = classify_lead_priority(30.0)
    assert res["tier"] == "NURTURE_TRACK"
    assert res["sla_hours"] == 72


def test_classify_score_out_of_bounds():
    with pytest.raises(ValueError, match="between 0 and 100"):
        classify_lead_priority(-5.0)

    with pytest.raises(ValueError, match="between 0 and 100"):
        classify_lead_priority(105.0)


def test_rank_leads_by_urgency():
    leads = [
        {"id": "L1", "score": 30.0, "days_since_contact": 1},   # 72h SLA
        {"id": "L2", "score": 90.0, "days_since_contact": 0},   # 4h SLA
        {"id": "L3", "score": 70.0, "days_since_contact": 6},   # 12h SLA (escalated)
        {"id": "L4", "score": 60.0, "days_since_contact": 1},   # 24h SLA
    ]
    ranked = rank_leads_by_urgency(leads)
    assert [x["id"] for x in ranked] == ["L2", "L3", "L4", "L1"]
