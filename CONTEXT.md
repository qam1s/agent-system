# Agent System

Multi-agent harness with shared tool registry: one core runtime plus a registry of independent agents (roles) that work in groups when needed.

## Language

**Role**:
A named autonomous agent registered in the platform registry. Directly invocable on its own; callable as a tool by other agents.
_Avoid_: persona, hat, profile

**Supervisor**:
The top-level agent that classifies an incoming request and delegates it to roles through subagents-as-tools dispatch.
_Avoid_: master, orchestrator

**Skill**:
A SKILL.md capability package (instructions plus optional scripts, references, assets) mounted on an agent and loaded via progressive disclosure.
_Avoid_: plugin, extension

**Quality gate**:
Deterministic checks plus an LLM-as-judge rubric a role's draft must pass before execution or delivery; failure loops back to revision.
_Avoid_: validator, moderator

**Golden dataset**:
Versioned per-role input→expected pairs used for offline evaluation.
_Avoid_: test set, fixtures
