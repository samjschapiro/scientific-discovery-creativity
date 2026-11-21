"""Environment registry. Add a discovery environment by importing its ENV here."""

from src.time_capsule.environments.endosymbiosis import ENV as _endosymbiosis
from src.time_capsule.environments.fission import ENV as _fission
from src.time_capsule.environments.neutron import ENV as _neutron

REGISTRY = {env.name: env for env in (_neutron, _fission, _endosymbiosis)}


def get_environment(name: str):
    if name not in REGISTRY:
        raise ValueError(f"FATAL: unknown environment '{name}'. Known: {sorted(REGISTRY)}")
    return REGISTRY[name]


def validate_all() -> None:
    for env in REGISTRY.values():
        env.validate()
