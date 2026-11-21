"""Rendering the environment into prompt variants.

Three variants, which together give the incumbency delta (the project's core contrast):

  WITH_M     setting + observations + the incumbent account and its epicycles + data.
             Frame replacement: a plausible wrong frame is present and must be displaced.
  WITHOUT_M  setting + observations + data, no account. Pure abduction, no incumbent —
             the control that isolates how much a *stated* wrong frame suppresses the leap.
  CONTROL    the negative-control environment (incumbent is correct; reframing is over-reach).

The ask never announces an anomaly or names a frame; it asks for the held-out value and the
principle that fixes it. The anomaly lives in the observations, to be noticed, not flagged.
"""

from src.sci_twist.environment import TransferEnvironment


def _fmt(value) -> str:
    v = value.numerator if value.denominator == 1 else value
    return f"+{v}" if (value.denominator == 1 and value >= 0) else f"{v}"


def render_table(env: TransferEnvironment) -> str:
    lines = []
    for pair in sorted(env.given):
        lines.append(f"  {env.label(pair)} = {_fmt(env.given[pair])}")
    held = env.label(env.held_out)
    body = "\n".join(lines)
    return (
        f"The nine measured pairs (grams gained by the first bath):\n\n{body}\n\n"
        f"The tenth pair, {held}, has never been run."
    )


def _ask(env: TransferEnvironment) -> str:
    held = env.label(env.held_out)
    return (
        f"The assay house wishes to know, before running it, what {held} will be. "
        f"Give the value and the principle that fixes it."
    )


def render(env: TransferEnvironment, variant: str) -> str:
    if variant == "WITH_M":
        blocks = [env.setting, render_table(env), env.observations, env.incumbent_account, _ask(env)]
    elif variant == "WITHOUT_M":
        blocks = [env.setting, render_table(env), env.observations, _ask(env)]
    elif variant == "CONTROL":
        blocks = [env.setting, render_table(env), env.observations, env.incumbent_account, _ask(env)]
    else:
        raise ValueError(f"FATAL: unknown prompt variant '{variant}'")
    return "\n\n".join(b.strip() for b in blocks)


VARIANTS = ("WITH_M", "WITHOUT_M", "CONTROL")
