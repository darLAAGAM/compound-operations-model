> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._

# Punta de Flecha v4 — Async Cross-Model Adversarial Convergence

*v4: refactor async (job pattern). Resuelve el problema de MCP timeout en deliberaciones largas.*
*Creado: 11 abril 2026 — Diego Arroyo*
*v4 update: 19 abril 2026*

## Cambio crítico v3 → v4

**Problema en v3:** la deliberación tarda 5-15 min (7 rounds × 2 modelos × 30-90s/llamada). MCP HTTP request timeout (~60s) cortaba la conexión y el agente recibía error.

**Fix v4:** patrón async/job. Tool retorna `job_id` instantáneo. Deliberación corre en proceso background. Otro tool consulta estado.

```
ANTES (v3):
  agent → punta_de_flecha(question)
       → [bloqueado 5-15 min]
       → ❌ MCP timeout (~60s)

AHORA (v4):
  agent → punta_de_flecha(question)
       → instant return: {job_id: "abc123", status: "queued"}
  ...background runner ejecuta deliberación...
  agent → punta_de_flecha_status("abc123")  [polling cada 30-60s]
       → {status: "running", current_phase: "round_2_adversarial", progress: "5/N"}
  ...
  agent → punta_de_flecha_status("abc123")
       → {status: "completed", synthesis: "..."}
```

## Tools MCP

### `punta_de_flecha(question, context="", max_rounds=5)` — spawn
Returns instantly:
```json
{
  "job_id": "abc123",
  "status": "queued",
  "estimated_time_minutes": "5-15",
  "next_step": "Call punta_de_flecha_status('abc123') in 30-60s"
}
```

### `punta_de_flecha_status(job_id, include_full_rounds=False)` — poll
Returns current state:
- `status`: queued / running / completed / failed
- `current_phase`: data_gathering / round_0_independent / round_N_adversarial / fact_check / red_team / synthesis / done
- `progress`: e.g. "3/N"
- `rounds_summary`: previews of completed rounds (full text if `include_full_rounds=True`)
- `synthesis`: final result (only when status="completed")
- `error`: error message (only when status="failed")

### `punta_de_flecha_list(limit=10)` — recent jobs
Lista últimos N jobs con status, phase, progress.

## Protocolo de uso para agentes

```python
# 1. Spawn
result = punta_de_flecha("¿Deberíamos abrir tienda en Salamanca?")
job_id = json.loads(result)["job_id"]

# 2. Wait + poll (cada 60s, max 20 min)
import time
for attempt in range(20):
    time.sleep(60)
    status = json.loads(punta_de_flecha_status(job_id))
    if status["status"] in ("completed", "failed"):
        break
    print(f"  [{attempt+1}] {status['current_phase']} ({status['progress']})")

# 3. Get final synthesis
if status["status"] == "completed":
    print(status["synthesis"])
elif status["status"] == "failed":
    print(f"FAILED: {status.get('error')}")
```

## Arquitectura técnica

```
┌─────────────────────────────────────────────────────────┐
│ MCP TOOL: punta_de_flecha (server.py)                   │
│   1. Generate job_id (uuid)                             │
│   2. Write question/context to /var/lib/the company/.../job.txt│
│   3. spawn: nohup python3 runner.py JOB_ID ... &        │
│   4. Return job_id INSTANTLY (no waits)                 │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ BACKGROUND: runner.py (detached subprocess)              │
│   - Phase -1: data_gathering (brain + Exa)               │
│   - Phase 0: independent analysis (Claude + GPT)         │
│   - Phase 1-3: ADVERSARIAL FORZADO (no convergencia)    │
│   - Phase 4-N: convergence permitted                     │
│   - Phase fact-check                                     │
│   - Phase red team                                       │
│   - Phase synthesis                                      │
│                                                          │
│ Each phase writes to /var/lib/the company/.../{job_id}.json   │
└─────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ MCP TOOL: punta_de_flecha_status                         │
│   - Reads {job_id}.json                                  │
│   - Returns current state (instant, no waits)           │
└─────────────────────────────────────────────────────────┘
```

## Ficheros

| Path | Propósito |
|---|---|
| `<your-services-dir>/adversarial-deliberation/runner.py` | Background runner (deliberación completa) |
| `<your-services-dir>/adversarial-deliberation/mcp_patch.py` | Patch script aplicado a server.py |
| `<your-mcp-server>/server.py` | 3 tools MCP (spawn, status, list) |
| `/var/lib/the company/punta_de_flecha/{job_id}.json` | State de cada job |
| `/var/lib/the company/punta_de_flecha/{job_id}.question.txt` | Pregunta del job |
| `/var/lib/the company/punta_de_flecha/{job_id}.context.txt` | Contexto del job |
| `/var/lib/the company/punta_de_flecha/{job_id}.log` | Log del subprocess |

## Cuándo usar Punta de Flecha

| Situación | Tool |
|-----------|------|
| Pregunta rápida táctica (<5 min) | Respuesta directa |
| Pregunta estratégica estándar (~10 min) | `council_query` (sync, 6 perspectivas single model) |
| Decisión de alto impacto (>€50K, irreversible) | **`punta_de_flecha`** (async, cross-model + RAG + red team) |
| Análisis máxima precisión | **`punta_de_flecha`** |
| Datos complejos/contradictorios | **`punta_de_flecha`** |

## Diagnóstico de calidad de la deliberación

| Convergencia en | Interpretación |
|-----------------|----------------|
| Round 1-2 | ⚠️ Demasiado blando (forbidden por v2+) |
| Round 3-4 | ✅ Zona óptima |
| Round 5-6 | ✅ Complejidad genuina |
| Sin convergencia Round 7 | ✅ Divergencias irresolubles = insight valioso |

| Fact-check | Interpretación |
|-----------|----------------|
| >70% verificado | ✅ Análisis bien fundamentado |
| 30-70% verificado | 🟡 Mixto, revisar inferencias |
| <30% verificado | ❌ Análisis basado en vibes |

| Red team | Interpretación |
|---------|----------------|
| Encuentra agujero fatal | 🔴 Re-deliberar con nueva info |
| CONSENSO VALIDADO | ✅ Robusto |

## Origen

Metodología desarrollada por Diego Arroyo (abril 2026). Inspirada en el protocolo de Javilop ([@javilop](https://x.com/javilop)) para análisis médico cross-model. Adaptada a estrategia business y generalizada como skill público en GitHub: https://github.com/darLAAGAM/punta-de-flecha

v1: básico. v2: adversarial forzado. v3: RAG + fact-check + red team. v4: async job pattern (resuelve MCP timeouts).
