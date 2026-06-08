"""Parallel orchestrator — respects factory.yml max_parallel via asyncio.Semaphore.

v0.9.0 ran all sub-agents sequentially. v0.9.1 builds a dependency graph
from declared inputs/outputs, identifies which sub-agents can run in
parallel (no shared dependencies), and dispatches them concurrently up
to max_parallel.

Strategy:
  - A sub-agent can run as soon as all its declared `inputs` are present
    in the shared context.
  - At each dispatch round, find all currently-runnable sub-agents.
  - Run up to `max_parallel` of them concurrently.
  - When any finishes, merge its output into context and re-evaluate.

This is a simple wave-scheduler — not full topological sort, but correct
for the CS factory's shape (early sub-agents have disjoint inputs, later
ones depend on earlier outputs).
"""
from __future__ import annotations
import asyncio
import time
from typing import Iterable

from operai_init.factory_runtime.config    import FactoryConfig, SubAgentConfig
from operai_init.factory_runtime.executor  import execute, SubAgentResult
from operai_init.factory_runtime.orchestrator import OrchestrationResult


def _runnable(
    sub_agent: SubAgentConfig,
    context: dict,
    already_run: set[str],
) -> bool:
    if sub_agent.name in already_run:
        return False
    for key in sub_agent.inputs:
        if key not in context:
            return False
    return True


async def _execute_async(
    sub_agent: SubAgentConfig,
    fc: FactoryConfig,
    input_dict: dict,
    mock: bool,
    semaphore: asyncio.Semaphore,
) -> SubAgentResult:
    async with semaphore:
        # execute() is sync (blocking urllib); run in thread to avoid blocking the event loop
        return await asyncio.to_thread(execute, sub_agent, fc, input_dict, mock=mock)


def _build_input(sub_agent: SubAgentConfig, context: dict) -> dict:
    return {k: context.get(k) for k in sub_agent.inputs}


async def run_once_parallel_async(
    fc: FactoryConfig,
    event: dict,
    *,
    mock: bool = False,
    max_parallel: int | None = None,
    limit: int | None = None,
) -> OrchestrationResult:
    """Parallel dispatch variant. Returns the same OrchestrationResult as sequential."""
    mp = max_parallel if max_parallel is not None else int(fc.orchestration.get("max_parallel", 3) or 3)
    semaphore = asyncio.Semaphore(mp)

    context = dict(event)
    result = OrchestrationResult(
        domain=fc.domain,
        factory_version=fc.version,
        event=dict(event),
        context=context,
    )
    t_start = time.time()

    sub_agents = fc.sub_agents
    if limit is not None:
        sub_agents = sub_agents[:limit]

    already_run: set[str] = set()
    done_count = 0

    while done_count < len(sub_agents):
        runnable = [
            sa for sa in sub_agents
            if sa.name not in already_run and _runnable(sa, context, already_run)
        ]
        if not runnable:
            # Nothing can progress. Either dependencies are missing (input-field not
            # emitted by any prior sub-agent) or we have a genuine stuck state.
            # For v0.9.1: break and run remaining as best-effort with whatever context we have.
            remaining = [sa for sa in sub_agents if sa.name not in already_run]
            for sa in remaining:
                res = await _execute_async(sa, fc, _build_input(sa, context), mock, semaphore)
                result.sub_agent_trace.append(res)
                already_run.add(sa.name)
                done_count += 1
                if res.ok:
                    for k, v in res.output_dict.items():
                        context[k] = v
                else:
                    result.errors.append(f"{sa.name}: {res.error}")
            break

        # Dispatch this wave in parallel
        wave_tasks = [
            _execute_async(sa, fc, _build_input(sa, context), mock, semaphore)
            for sa in runnable
        ]
        wave_results = await asyncio.gather(*wave_tasks)
        for sa, res in zip(runnable, wave_results):
            result.sub_agent_trace.append(res)
            already_run.add(sa.name)
            done_count += 1
            if res.ok:
                for k, v in res.output_dict.items():
                    context[k] = v
            else:
                result.errors.append(f"{sa.name}: {res.error}")

    result.total_latency_ms = int((time.time() - t_start) * 1000)
    result.total_cost_usd = sum(r.cost_usd for r in result.sub_agent_trace)

    escalation = next((r for r in result.sub_agent_trace if r.name == "escalation-scorer" and r.ok), None)
    if escalation:
        result.final_action    = escalation.output_dict.get("action", "unknown")
        result.final_rationale = escalation.output_dict.get("rationale", "")
    drafter = next((r for r in result.sub_agent_trace if r.name == "drafter" and r.ok), None)
    if drafter:
        result.draft_reply = drafter.output_dict.get("draft_reply", "")

    result.ok = all(r.ok for r in result.sub_agent_trace)
    return result


def run_once_parallel(
    fc: FactoryConfig,
    event: dict,
    *,
    mock: bool = False,
    max_parallel: int | None = None,
    limit: int | None = None,
) -> OrchestrationResult:
    """Sync wrapper for the async variant."""
    return asyncio.run(run_once_parallel_async(fc, event, mock=mock, max_parallel=max_parallel, limit=limit))
