import pytest

from sicl.copilot_contract import CopilotFact, FactStatus
from sicl.copilot_design import (
    AlternativeScore, CriterionDirection, DesignAlternative, DesignBrief, DesignCriterion,
)


def criteria():
    return (
        DesignCriterion("access", "Accessibility", "Access and walkability", 0.4, CriterionDirection.MAXIMIZE),
        DesignCriterion("cost", "Cost", "Construction cost", 0.6, CriterionDirection.MINIMIZE, unit="PEN"),
    )


def alt():
    return DesignAlternative("a1", "Alternative A", "Mixed-use connected plaza",
                           scores=(AlternativeScore("access", 0.8, 0.8), AlternativeScore("cost", 100, 0.6)))


def brief(**kw):
    base=dict(brief_id="b1",project_id="p1",created_at="2026-11-26T10:00:00Z",
              title="Urban renewal",purpose="Improve public realm",facts=(CopilotFact("area",value=5000,status=FactStatus.CONFIRMED,source="survey"),),
              criteria=criteria(),alternatives=(alt(),))
    base.update(kw)
    return DesignBrief(**base)


def test_valid_design_brief_tracks_facts_and_weighted_criteria():
    item=brief()
    assert sum(c.weight for c in item.criteria)==pytest.approx(1.0)
    assert item.alternatives[0].scores[0].criterion_id=="access"


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError,match="sum to 1"):
        brief(criteria=(DesignCriterion("x","X","x",0.2,CriterionDirection.MAXIMIZE),))


def test_target_criterion_requires_target_value():
    with pytest.raises(ValueError,match="requires target"):
        DesignCriterion("target","Target","",0.5,CriterionDirection.TARGET)


def test_alternative_cannot_score_unknown_criterion():
    bad=DesignAlternative("b2","Bad","concept",scores=(AlternativeScore("unknown",1),))
    with pytest.raises(ValueError,match="unknown criteria"):
        brief(alternatives=(bad,))


def test_alternative_scores_are_bounded_when_normalized():
    with pytest.raises(ValueError,match="normalized_score"):
        AlternativeScore("access",1,normalized_score=2)


def test_duplicate_criteria_rejected():
    with pytest.raises(ValueError,match="duplicate criterion"):
        brief(criteria=(criteria()[0],criteria()[0]))
