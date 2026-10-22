from __future__ import annotations

from dataclasses import asdict

from .domain import Actor, ActorPosition


def actor_to_dict(actor: Actor) -> dict:
    value = asdict(actor)
    value["role"] = actor.role.value
    value["authority_level"] = actor.authority_level.value
    value["state"] = actor.state.value
    value["created_at"] = actor.created_at.isoformat()
    return value


def position_to_dict(position: ActorPosition) -> dict:
    value = asdict(position)
    value["subject_type"] = position.subject_type.value
    value["stance"] = position.stance.value
    value["created_at"] = position.created_at.isoformat()
    return value
