"""operai-init llm — CLI for LLM provider configuration + usage + testing."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from operai_init import common
from operai_init.llm import config, registry, usage
from operai_init.llm import client as llm_client
from operai_init.llm.providers._http import ProviderHTTPError


def cmd_list(args, *, home: Path, brand: str):
    configured = set(config.list_configured(home))
    default = config.get_default(home)

    print(f"\n  {common.BOLD}LLM providers{common.RESET}\n")
    print(f"  {'PROVIDER':<12} {'STATUS':<14} {'LAST TEST':<22} {'MODELS':<}")
    print(f"  {'-'*12} {'-'*14} {'-'*22} {'-'*30}")
    for name, spec in registry.REGISTRY.items():
        models = ", ".join(spec.models.keys())
        is_conf = name in configured
        data = config.load(home).get("providers", {}).get(name, {})
        status = "configured" if is_conf else "not configured"
        last_test = ""
        if data.get("last_test_ok"):
            last_test = data["last_test_ok"][:19]
        elif data.get("last_test_error"):
            last_test = f"{common.RED}error{common.RESET}"
        color = common.GREEN if is_conf else common.DIM
        print(f"  {color}{name:<12}{common.RESET} {status:<14} {last_test:<22} {common.DIM}{models}{common.RESET}")

    if default:
        print(f"\n  {common.BOLD}Default:{common.RESET} {default['provider']}/{default['model']}")
    else:
        print(f"\n  {common.GOLD}!{common.RESET} No default set — agents will refuse to start. Run: operai-init llm set-default")
    print()


def cmd_configure(args, *, home: Path, brand: str):
    target = args.provider
    if target and target not in registry.REGISTRY:
        common.err(f"unknown provider '{target}' — available: {list(registry.REGISTRY.keys())}")
        return

    common.banner("Configure LLM providers")
    providers_to_setup = [target] if target else list(registry.REGISTRY.keys())

    for p in providers_to_setup:
        spec = registry.REGISTRY[p]
        existing = config.get_api_key(home, p)
        print(f"\n  {common.BOLD}{p}{common.RESET}")
        print(f"  Models: {', '.join(spec.models.keys())}")
        print(f"  Env var: {spec.env_var}")
        if existing:
            if not common.confirm(f"  Already configured. Re-configure?", default=False):
                continue
        print(f"  Where to get a key: https://{'platform.openai.com/api-keys' if p=='openai' else 'console.anthropic.com/settings/keys' if p=='anthropic' else 'aistudio.google.com/apikey' if p=='gemini' else 'dashscope.console.aliyun.com' if p=='qwen' else 'minimaxi.com/login'}")
        key = common.read_secret(f"  {p} API key (paste, input hidden, empty to skip): ").strip()
        if not key:
            common.info(f"  skipped {p}")
            continue
        config.set_provider(home, p, key)
        common.ok(f"  {p} configured")
        if common.confirm("  Test now?", default=True):
            _test_provider(home, p)

    # Offer to set default if none set
    if not config.get_default(home):
        configured = config.list_configured(home)
        if configured:
            p = configured[0]
            m = registry.REGISTRY[p].default_model
            if common.confirm(f"\n  No default set. Use {p}/{m} as default?", default=True):
                config.set_default(home, p, m)
                common.ok(f"default set to {p}/{m}")


def cmd_test(args, *, home: Path, brand: str):
    target = args.provider
    if target not in registry.REGISTRY:
        common.err(f"unknown provider '{target}'")
        return
    _test_provider(home, target)


def _test_provider(home: Path, provider: str) -> bool:
    spec = registry.REGISTRY[provider]
    api_key = config.get_api_key(home, provider)
    if not api_key:
        common.err(f"{provider} not configured")
        return False
    common.info(f"testing {provider}/{spec.test_model}…")
    try:
        resp = llm_client.chat(
            system="Reply with exactly the word: pong",
            user="ping",
            provider=provider,
            model=spec.test_model,
            max_tokens=10,
            temperature=0.0,
            caller=f"operai-init llm test {provider}",
        )
    except ProviderHTTPError as e:
        common.err(f"{provider} test failed: HTTP {e.status} — {str(e.body)[:200]}")
        config.mark_tested(home, provider, ok=False, error=str(e))
        return False
    except Exception as e:  # noqa: BLE001
        common.err(f"{provider} test failed: {e}")
        config.mark_tested(home, provider, ok=False, error=str(e))
        return False
    common.ok(f"{provider} OK · reply={resp.text[:60]!r} · tokens={resp.tokens_in}/{resp.tokens_out} · ${resp.cost_usd:.6f} · {resp.latency_ms}ms")
    config.mark_tested(home, provider, ok=True)
    return True


def cmd_set_default(args, *, home: Path, brand: str):
    if args.provider not in registry.REGISTRY:
        common.err(f"unknown provider '{args.provider}'")
        return
    spec = registry.REGISTRY[args.provider]
    model = args.model or spec.default_model
    if model not in spec.models:
        common.err(f"provider {args.provider} has no model '{model}'. Available: {list(spec.models.keys())}")
        return
    if args.provider not in config.list_configured(home):
        common.err(f"{args.provider} not configured yet. Run: operai-init llm configure {args.provider}")
        return
    config.set_default(home, args.provider, model)
    common.ok(f"default set to {args.provider}/{model}")


def cmd_fallback(args, *, home: Path, brand: str):
    chain = []
    for item in args.chain:
        if "/" not in item:
            common.err(f"invalid entry '{item}' — use provider/model format")
            return
        p, m = item.split("/", 1)
        if p not in registry.REGISTRY or m not in registry.REGISTRY[p].models:
            common.err(f"unknown provider/model: {item}")
            return
        chain.append({"provider": p, "model": m})
    config.set_fallback_chain(home, chain)
    chain_str = " → ".join(f"{c['provider']}/{c['model']}" for c in chain)
    common.ok(f"fallback chain: {chain_str}")


def cmd_remove(args, *, home: Path, brand: str):
    if config.remove_provider(home, args.provider):
        common.ok(f"removed {args.provider}")
    else:
        common.warn(f"{args.provider} was not configured")


def cmd_usage(args, *, home: Path, brand: str):
    report = usage.summary(home, since_days=args.since)
    if args.json:
        print(json.dumps(report, indent=2))
        return
    print(f"\n  {common.BOLD}LLM usage — last {args.since} days{common.RESET}\n")
    if not report["rows"]:
        common.info("no calls recorded yet")
        return
    print(f"  {'PROVIDER':<12} {'MODEL':<18} {'CALLS':>7} {'TOK_IN':>10} {'TOK_OUT':>10} {'USD':>9}")
    print(f"  {'-'*12} {'-'*18} {'-'*7} {'-'*10} {'-'*10} {'-'*9}")
    for r in report["rows"]:
        print(f"  {r['provider']:<12} {r['model']:<18} {r['calls']:>7} {r['tokens_in']:>10,} {r['tokens_out']:>10,} ${r['cost_usd']:>8.4f}")
    print(f"\n  Total: {report['total_calls']} calls, ${report['total_cost_usd']:.2f}")
    errs = usage.recent_errors(home, limit=5)
    if errs:
        print(f"\n  {common.BOLD}Recent errors{common.RESET}")
        for e in errs:
            print(f"    {e['ts'][:19]}  {e['provider']}/{e['model']}  {common.DIM}{e['caller']}{common.RESET}")
            print(f"      {common.RED}{(e['error'] or '')[:150]}{common.RESET}")
    print()


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("llm", help="Manage LLM providers (configure / test / usage)")
    inner = p.add_subparsers(dest="llm_action", required=True)

    sp = inner.add_parser("list", help="List providers + configured status")
    sp.set_defaults(llm_func=cmd_list)

    sp = inner.add_parser("configure", help="Interactively configure one or all providers")
    sp.add_argument("provider", nargs="?", choices=list(registry.REGISTRY.keys()))
    sp.set_defaults(llm_func=cmd_configure)

    sp = inner.add_parser("test", help="Ping a provider with a test call")
    sp.add_argument("provider", choices=list(registry.REGISTRY.keys()))
    sp.set_defaults(llm_func=cmd_test)

    sp = inner.add_parser("set-default", help="Set the brand-wide default provider + model")
    sp.add_argument("--provider", required=True)
    sp.add_argument("--model", help="Model alias (default: provider's default)")
    sp.set_defaults(llm_func=cmd_set_default)

    sp = inner.add_parser("fallback", help="Set fallback chain (ordered)")
    sp.add_argument("chain", nargs="+", help="provider/model entries, e.g. openai/gpt-4o-mini groq/llama-3.3-70b")
    sp.set_defaults(llm_func=cmd_fallback)

    sp = inner.add_parser("remove", help="Remove a provider configuration")
    sp.add_argument("provider", choices=list(registry.REGISTRY.keys()))
    sp.set_defaults(llm_func=cmd_remove)

    sp = inner.add_parser("usage", help="Usage summary (tokens + cost per provider)")
    sp.add_argument("--since", type=int, default=30, help="Lookback days (default 30)")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(llm_func=cmd_usage)
