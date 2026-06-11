> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._

# Codex Handoff — Delegación Claude → Codex con prompt self-contained

*Creado: 19 mayo 2026 — Diego Arroyo*
*Operacionaliza: `knowledge/platform/agents/role-boundaries.md` (formalizado 27-abr-2026)*
*Encaja con: REGLA 8 (triage) + REGLA 11 (Brain+Skills review) del prompt maestro*

---

## Qué es

Skill operativo que **convierte el principio "Claude orquesta, Codex ejecuta técnico" en un flujo ejecutable step-by-step**. No es documento de filosofía — es checklist + templates + comandos exactos para delegar bien a la primera.

**Objetivo:** eliminar el anti-pattern "Claude hace 200+ tool calls de código sin delegar" (Diego espera 3h cuando podría haber sido 30 min vía Codex).

---

## Cuándo invocar

| Situación | Trigger fuerte |
|-----------|----------------|
| Script >30 líneas o sync pipeline completo | "delega a Codex", "esto es para Codex" |
| Debug técnico >30 min sin progreso | auto: tras 1 intento Claude fallido, STOP y handoff |
| Bulk processing (batch ops, data migration) | siempre Codex |
| Adversarial review de plan propio (Punta de Flecha) | siempre Codex (sesgo confirmación) |
| Refactor multi-file | siempre Codex |
| Code review pre-commit profundo | siempre Codex |
| Análisis técnico que requiere `model_reasoning_effort="high"` | siempre Codex |

**No invocar para:** edits <10 líneas, brain_writes, conversación estratégica, síntesis, decisiones, doc canonical <50 líneas. Eso es trabajo de orquestador.

---

## Protocolo de ejecución (5 fases, 5-45 min según task)

### Fase 1 — Formular prompt SELF-CONTAINED (~5 min)

Codex no ve tu conversación con Diego. El prompt debe contener TODO el contexto necesario.

**Path:** `/tmp/codex-task-YYYYMMDD-HHMMSS.md`

**Template obligatorio:**

```markdown
# Task: <título corto y específico>

## Contexto

<3-5 frases sobre the company/sistema relevantes para esta tarea>
<Paths absolutos a archivos clave>
<Versión software/API/MCP si importa>
<Credenciales como variables de entorno: $TOKEN, no el valor>

## Objetivo

<Qué entregar, en una frase>

## Criterios de éxito

- <Medible 1: e.g. "test pasa con curl X"; "output file existe en /tmp/Y"; "logs muestran Z">
- <Medible 2>
- <Medible 3>

## Constraints

- Archivos que puede editar: <lista>
- Archivos que NO debe tocar: <lista>
- NO commitear (Diego revisa antes)
- NO ejecutar deletes destructivos sin confirmación

## Formato output esperado

<Cómo Codex debe devolver el resultado>
<E.g. "Imprime al final un bloque ```RESULT``` con el diff aplicado y status">
```

**Anti-patrón:** "Aquí tienes los archivos relevantes, haz lo que creas mejor". → Codex devuelve análisis genérico. Sé explícito.

### Fase 2 — Ejecutar Codex (~30 seg setup, N min ejecución)

⚠️ **Path absoluto obligatorio.** Aliases `.zshrc` no se expanden en non-interactive shells.

```bash
TS=$(date +%Y%m%d-%H%M%S)
PROMPT=/tmp/codex-task-$TS.md
OUT=/tmp/codex-out-$TS.txt

# Lanzar en background
nohup /opt/homebrew/bin/codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  --skip-git-repo-check \
  --color never \
  < $PROMPT \
  > $OUT 2>&1 &

PID=$!
echo "Codex PID=$PID, output=$OUT"
```

### Fase 3 — Monitor (~ depende task)

NO polling manual. NO `sleep 60 && cat`. Usa Bash `run_in_background` o Monitor tool:

```bash
# Esperar hasta que el proceso termine (notificación automática)
until ! kill -0 $PID 2>/dev/null; do sleep 30; done
echo "Codex DONE"
```

Si va a tardar >5 min: usa `ScheduleWakeup` o `run_in_background=true` para no quemar cache window.

### Fase 4 — Leer + validar (~3-5 min)

```bash
# Leer output
tail -200 $OUT
```

Verifica criterios de éxito uno a uno. Si Codex devolvió algo ambiguo:

- **NO** copiar raw a Diego.
- **SÍ** validar tú mismo: leer archivos modificados con Read, correr tests si aplica, confirmar logs.

**Decisión:**

| Resultado | Acción |
|-----------|--------|
| Todos los criterios ✅ | Pasa a Fase 5 |
| Algún criterio falló | Iterar: prompt nuevo con feedback específico ("falló X porque Y, corrige Z") |
| Codex pidió clarificación | Responde con nuevo prompt-task más completo |
| Codex hizo lo opuesto a lo pedido | Prompt original era ambiguo → reescribir |

### Fase 5 — Sintetizar para Diego + documentar (~3 min)

**NO copiar el output de Codex al chat con Diego.** Sintetiza.

Template síntesis:

```
## Resultado Codex

**Tarea:** <título>
**Tiempo:** N min
**Status:** ✅ done / ⚠️ parcial / ❌ blocked

**Hecho:**
- <bullet accionable 1>
- <bullet accionable 2>

**Validado por mí:**
- <verificación 1>
- <verificación 2>

**Pendiente / decisiones para Diego:**
- <decisión 1>

**Output completo:** `/tmp/codex-out-<TS>.txt` (N KB) si quieres ver raw.
```

Si tarea generó knowledge nuevo (gotcha, pattern, decision, bug) → `brain_write` automático.

---

## Templates por tipo de tarea

### A) Script nuevo (>30 líneas)

```markdown
# Task: Script <nombre>

## Contexto
Sistema the company. Necesito script Python que <propósito>.
Stack: Python 3.11, libs disponibles via `pip` ya instaladas.
Credenciales: $TOKEN_X en env.

## Objetivo
Crear `/path/to/script.py` que <comportamiento>.

## Criterios de éxito
- Script ejecutable: `python3 /path/to/script.py --help` muestra usage
- Caso éxito: `python3 /path/to/script.py <input>` produce <output esperado>
- Caso error: input inválido → exit code 1 con mensaje claro

## Constraints
- Usar logging estándar (no print)
- Type hints en signatures
- Sin dependencias nuevas (verifica con pip list)

## Output
Imprime al final el path del script + ejemplo de invocación + sample output.
```

### B) Debug profundo (>30 min)

```markdown
# Task: Debug <error/comportamiento>

## Contexto
<descripción del bug observado>
<reproducción exacta: comando + input + output observado vs esperado>
Stack: <versions relevantes>
Logs disponibles en: <path>

## Objetivo
Root cause + fix aplicado + test que previene regresión.

## Criterios de éxito
- Root cause documentado en 2-3 frases
- Fix aplicado a <archivo>
- Test (o repro manual) que falla antes del fix y pasa después
- Documentación en `knowledge/platform/gotchas/<slug>-YYYY-MM-DD.md`

## Constraints
- No tocar <archivos protegidos>
- Si el fix requiere migration → para y reporta, no ejecutes solo

## Output
```RESULT
ROOT CAUSE: ...
FIX APLICADO: <diff>
TEST: <comando>
GOTCHA DOC: <path>
```
```

### C) Adversarial review (Punta de Flecha)

```markdown
# Task: Adversarial review de plan X

## Contexto
Diego está considerando hacer <X>. Mi (Claude) recomendación inicial es <Y> por razones <Z>.

Plan completo: `/tmp/plan-XXX.md` (anexado).

Quiero que asumas el rol de adversario: encuentra agujeros, edge cases, costes ocultos, supuestos no verificados.

## Objetivo
Lista de 5-10 críticas reales al plan, ordenadas por severidad.

## Criterios de éxito
- Cada crítica cita una sección específica del plan
- Cada crítica propone qué evidencia falta para descartarla
- Al menos 2 críticas son tipo "este supuesto no está verificado"
- Al menos 1 crítica es tipo "esto es estructuralmente flawed"

## Output
```REVIEW
1. [SEVERIDAD ALTA] <crítica> — sección X del plan — evidencia a buscar: <Y>
2. ...
```

Recomendación final: ✅ procede / ⚠️ procede con cambios <Z> / ❌ replantear
```

### D) Bulk processing

```markdown
# Task: Procesar <N items>

## Contexto
Tengo <N> items en <path / DB / API>. Necesito <transformación> por cada uno.

## Objetivo
Script + ejecución que procesa todos los items y devuelve <output>.

## Criterios de éxito
- 100% items procesados o reporte explícito de fallidos
- Idempotente (re-ejecutar no rompe nada)
- Logs por item con timestamp
- Estado guardado en <path> para resumability

## Constraints
- Rate limit: max <N> req/min a <API>
- Timeout per item: 30s
- Si falla >10% items → STOP y reporta

## Output
```RESULT
Procesados: N/M (X%)
Fallidos: lista con razón
Output guardado: <path>
Tiempo total: N min
```
```

---

## Anti-patterns (lo que ROMPE el handoff)

| ❌ Mal | ✅ Bien |
|--------|---------|
| Prompt vago: "haz el sync de X" | Prompt SELF-CONTAINED: contexto + objetivo + criterios + output esperado |
| Usar `codex exec` con alias `cxe` | Path absoluto `/opt/homebrew/bin/codex` (aliases no se expanden) |
| Lanzar foreground y bloquear chat | `nohup ... &` + monitor async |
| Copiar raw output de Codex (50KB de logs) a Diego | Sintetizar a 5-10 bullets accionables |
| Marcar task done sin validar criterios uno a uno | Cada criterio verificado por Claude antes de cerrar |
| Iterar con Codex sin reescribir prompt completo | Nuevo prompt task con feedback específico + criterios revisados |
| Delegar todo "por si acaso" | Solo lo que cumple triggers fuertes; el resto lo hace Claude |
| No documentar decisión técnica | `brain_write` automático tras Fase 5 si hay knowledge nuevo |
| Olvidar Punta de Flecha en planes propios grandes | Adversarial review SIEMPRE via Codex (sesgo confirmación) |

---

## Checklist rápido

```
□ Fase 1 — Prompt SELF-CONTAINED en /tmp/codex-task-<TS>.md (template A/B/C/D)
□ Fase 2 — Lanzado con nohup + path absoluto Codex
□ Fase 3 — Monitor async (no polling manual)
□ Fase 4 — Output validado contra criterios uno a uno
□ Fase 5 — Síntesis a Diego (no raw) + brain_write si hay knowledge nuevo
```

---

## Ejemplos de uso

### Ejemplo 1: Codex bien delegado (~30 min total)

```
Diego: necesito un sync de events GA4 a BigQuery, daily, idempotente.

Claude: 
  → Esto es script + sync pipeline = Codex.
  → Formulo prompt template A en /tmp/codex-task-20260519-103045.md
  → Lanzo nohup
  → Monitor 25 min
  → Validato: script existe, --help funciona, dry-run procesa 1 event OK
  → Síntesis a Diego: "✅ sync.py en /path. Tested dry-run con 1 event. 
     systemd timer configurado daily 03:00. Pendiente: tu OK para activar."
  → brain_write a knowledge/platform/tools/ga4-bigquery-sync.md
```

### Ejemplo 2: Anti-pattern (Master Calendar 24-abr-2026, hizo Claude solo)

```
Diego: build el Master Calendar en Notion con 12 vistas + sync script
Claude (mal): empezó a hacer 200+ tool calls de código. 3h después...
Diego: esto te ha llevado 3h. Codex en effort=high lo habría hecho en 30 min.

→ Esta es exactamente la situación que esta skill viene a prevenir.
```

### Ejemplo 3: Iteración (1 vez sin éxito → re-prompt mejor)

```
Iter 1: Prompt vago "implementa retry logic". Codex devuelve solo 1 nivel retry.
Iter 2: Re-prompt: "retry exponencial 3 niveles (1s, 4s, 16s), max 3 attempts,
        log cada retry con WARN, raise tras 3 fallos consecutivos".
Codex iter 2: ✅ implementado correctamente.

Lección: cada iteración fallida → reescribir prompt con criterios más específicos,
no "dale otra vuelta" genérico.
```

---

## Cross-references

- Role boundaries (filosofía + ejemplos cronológicos): `knowledge/platform/agents/role-boundaries.md`
- Swarm propagation (skill complementaria): `knowledge/skills/swarm-propagation/SKILL.md`
- Punta de Flecha (uso específico para adversarial): `knowledge/skills/punta-de-flecha/SKILL.md`
- Suggest-skills (qué hacer al cierre): `knowledge/skills/suggest-skills/SKILL.md`
- REGLA 8 (triage de tarea): prompt maestro v1.8 sección 8
- REGLA 11 (Brain+Skills review): `knowledge/platform/rules/brain-skills-review-before-execution.md`

---

## Cambios

| Fecha | Cambio | Por |
|-------|--------|-----|
| 2026-05-19 | Skill creada para operacionalizar role-boundaries.md. ROI estimado ~5 handoffs/mes × 12 min ahorrados/handoff (vs prompts mal formulados) = 1h/mes + outputs mucho mejores. | Claude Code |
