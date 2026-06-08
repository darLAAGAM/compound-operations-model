"""operai_init.factory_runtime — sub-agent dispatcher (v0.9.0).

Scope v0.9.0:
  - `operai-init factory run-once --domain <d> --input <path>` entry point
  - Sequential sub-agent execution (parallel comes in v0.9.1)
  - No event bus / daemon / webhook receiver — manual invocation only
  - Mock-LLM mode for offline smoke tests (`--mock-llm`)
  - Markdown trace to stdout or file

Not in v0.9.0:
  - Parallel execution
  - Event queue daemon
  - Webhook receivers
  - Action executor (we print the recommendation, don't act on it)
  - Brain auto-lookup (inputs must be pre-loaded in the ticket JSON)
  - Cost budget enforcement
  - Retries on transient errors
"""
__version__ = "0.9.0"
