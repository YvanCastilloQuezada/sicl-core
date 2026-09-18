from dataclasses import asdict

from sicl.multi_agent_design import debate, design_critic, multi_agent_exploration, position_matrix
from sicl.spatial_generator import generate_upao001_alternatives


def alt():
    return asdict(generate_upao001_alternatives()[0])


def test_same_design_is_inspected_by_supported_scope_agents():
    result = multi_agent_exploration(alt(), "edificacion")
    assert result["exploration"]["alternative_id"] == alt()["alternative_id"]
    assert result["agent_winner"] is None
    assert result["decision_created"] is False
    assert any(item.get("classification") == "AGENT_INTERPRETATION" for item in result["exploration"]["observations"])


def test_position_matrix_preserves_disagreement_and_critic_is_non_decisional():
    result = multi_agent_exploration(alt(), "edificacion")
    matrix = position_matrix(result["exploration"])
    critic = design_critic(result["exploration"])
    assert matrix["disagreement_preserved"] is True
    assert matrix["majority_vote_decision"] is False
    assert critic["automatic_decision"] is False


def test_debate_can_remain_unresolved_and_requires_human_review():
    result = multi_agent_exploration(alt(), "edificacion")
    debate_result = debate("gross_massing_area", result["exploration"], result["position_matrix"])
    assert debate_result["unresolved_allowed"] is True
    assert debate_result["human_review_required"] is True
    assert debate_result["decision_created"] is False
