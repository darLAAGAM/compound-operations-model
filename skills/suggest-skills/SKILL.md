> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._

# Suggest Skills — Meta-skill para harvestear patrones y proponer skills nuevas

*Creado: 19 mayo 2026 — Diego Arroyo*
*Inspirado en patrón `/skillify` de Garry Tan (GBrain) — "if I have to ask you for something twice, you failed"*
*Encaja con: Eje 3 plan brain v2 + REGLA 11 del prompt maestro*

---

## Qué es

Meta-skill **invocable mid-conversación** que:
1. **Audita** los últimos turnos de la conversación viva
2. **Cross-checkea** vs las 170+ skills existentes en el brain
3. **Propone** skills nuevas a crear + mejoras a existentes + lo que NO merece skill

**Objetivo:** cada sesión productiva del swarm o del equipo deja una huella de mejora del sistema, no solo output. El brain se vuelve compounding (Garry Tan pattern).

---

## Cuándo invocar

| Situación | Trigger |
|-----------|---------|
| Conversación larga donde Claude hizo trabajo no-trivial | `/suggest-skills` o "suggest skills" |
| Final de sesión productiva (decisión, bug, pattern, workflow) | "review what we did, suggest skills" |
| Reinventaste un proceso 2+ veces en mismas semanas | "qué skills harían falta para no repetir esto" |
| Antes de un proyecto grande nuevo | "qué skills ya tenemos relacionadas + qué falta" |
| Diego o cualquier owner audita uso del brain | "audit my skill usage this week" |

**Anti-pattern:** invocar cada 5 minutos. Esta skill es para sesiones con ~15+ turnos o trabajo claramente skill-worthy.

---

## Protocolo de ejecución (3 fases, ~5-7 min)

### Fase 1 — Audit conversación viva (~2 min)

Lee últimos 15-30 turnos. Identifica:

- **Tareas repetidas:** ¿el usuario pidió 2+ veces algo similar?
- **Frustraciones:** ¿hubo "esto no funcionó", "otra vez", "como te dije antes"?
- **Workarounds:** ¿Claude tuvo que improvisar porque no había skill/tool específica?
- **Reinvención:** ¿Claude reconstruyó un proceso que probablemente ya existe?
- **Decisiones reusables:** ¿hubo metodología que aplicaría a casos similares?
- **Patterns:** ¿secuencia de tools/skills que se repitió en distintos puntos?

Para cada hallazgo, captura:
- Frase exacta del usuario o acción de Claude (evidencia)
- Frecuencia (1 vez / N veces / cada vez)
- Coste estimado de reinventarlo cada vez (minutos + tokens)

### Fase 2 — Cross-check vs skills existentes (~2 min)

Para cada hallazgo de Fase 1:

```python
# 1. Búsqueda exhaustiva en skills existentes
skill_search("<keyword del hallazgo>")
skill_search("<dominio + verbo>")

# 2. Para skills cercanas pero no exactas
skill_read("<skill_name>")  # ver si extiende o si necesita fork
```

Clasifica cada hallazgo en:
- **A) Skill existe y aplica directo** → el usuario no la usó por desconocimiento. Acción = educar, no crear
- **B) Skill cerca pero falta caso específico** → extender skill existente
- **C) Gap real, no hay skill** → candidata a skill nueva
- **D) No es recurrente, no merece skill** → descartar

### Fase 3 — Propone output estructurado

Devuelve 4 secciones (en este orden):

#### 🟢 NEW SKILLS (crear)

Solo si fase 2 categoría C. Por cada propuesta:

```
**Nombre:** <slug-en-kebab-case>
**Path sugerido:** knowledge/skills/<dominio>/<slug>/SKILL.md
**When to use:** <1 frase, trigger phrase>
**Ejemplo input:** <prompt real que la dispararía>
**Output esperado:** <qué devuelve>
**Tools/skills que combina:** <lista>
**Prioridad:** Alta/Media/Baja
**ROI estimado:** invocaciones/mes × tiempo ahorrado/invocación
**Time-to-create:** ~30 min / ~2h / ~1 día
**Evidence (de Fase 1):** "<quote>" — pasó N veces
```

#### 🟡 IMPROVE EXISTING (extender)

Solo si fase 2 categoría B. Por cada propuesta:

```
**Skill:** <skill_name>
**Cambio sugerido:** <qué añadir/modificar>
**Por qué:** <evidencia de Fase 1>
**Time-to-update:** ~10 min / ~30 min / ~1h
**Prioridad:** Alta/Media/Baja
```

#### 🔵 EDUCATE (skill ya existía)

Solo si fase 2 categoría A. Por cada:

```
**Hallazgo:** <qué hizo el usuario sin skill>
**Skill que aplicaba:** <skill_name>
**Acción:** documentar en `knowledge/the company/<owner>/gotchas/` que para casos X usar skill Y
**Quién debe saberlo:** <owner relevante: the digital lead, the marketing agent, etc.>
```

#### ⚪ NOT-WORTH (descartado)

Solo si fase 2 categoría D. Por cada:

```
**Patrón:** <descripción breve>
**Por qué no merece skill:** <one-shot / muy específico / ya cubierto por brain_search>
```

---

## Ejemplos de uso

### Ejemplo 1: Sesión productiva técnica

```
Usuario: hoy hemos: configurado Mobbin en todos los nodos, propagado tokens OAuth a VPS + Mac Mini, escrito 2 reglas obligatorias nuevas (REGLA 10 + REGLA 11), construido el sync script de prompt master. Suggest skills.

Claude (suggest-skills):

🟢 NEW SKILLS (3):

1. **propagate-mcp-to-swarm**
   Path: knowledge/skills/propagate-mcp-to-swarm/SKILL.md
   When to use: cuando se añade un MCP nuevo y hay que propagarlo a todos los nodos (Claude Code + Codex + Claude Desktop equipo + 8 agentes OpenClaw)
   Ejemplo input: "añade <new MCP url> a todos los nodos del swarm"
   Output: lista de paths actualizados + tests de conexión + memoria entry
   Time-to-create: ~30 min
   Prioridad: Alta (lo hicimos hoy con Mobbin, próxima vez evitamos reinventar)
   ROI: 2-3 invocaciones/año × 1h ahorrada = 3h/año

2. **propagate-oauth-tokens**
   Path: knowledge/skills/propagate-oauth-tokens/SKILL.md
   When to use: cuando un nuevo MCP requiere OAuth y queremos shared-auth (no auth per nodo)
   Trigger: "propaga los tokens OAuth de <MCP> a todos los nodos"
   ...

🟡 IMPROVE EXISTING (1):

1. **Skill:** prompt-maestro-claude (canon)
   Cambio: añadir sección "cómo se aplica en cada nodo" más estructurada
   ...

🔵 EDUCATE: (0 — nada que el usuario podría haber hecho con skill existente)

⚪ NOT-WORTH (1): "actualizar Notion onboarding" — uno-off, ya hecho.
```

### Ejemplo 2: Sesión productiva no técnica

```
Usuario: the digital lead y yo hemos pasado 2 horas analizando por qué bajó la conversión en mobile esta semana — pulled GA4, miramos Hotjar, comparamos con semana pasada, encontramos que un banner nuevo rompía el flow. Suggest skills.

Claude (suggest-skills):

🟢 NEW SKILLS (1):

1. **conversion-drop-investigation**
   Path: knowledge/skills/conversion-drop-investigation/SKILL.md
   When to use: cuando hay caída de conversión inesperada en tu ecommerce
   Trigger: "conversion drop investigation" / "por qué bajó conversión"
   Protocolo: GA4 baseline → Hotjar session replays → comparar diff vs semana previa → identificar deploys/cambios → hipótesis ranked
   Combina: ga4_query, brain_search, slack_search (deploys), hotjar (manual)
   ROI: ~2 invocaciones/mes × 2h ahorradas = 4h/mes (the digital lead + 1 más)
   Prioridad: Alta

🟡 IMPROVE EXISTING (1):

1. **Skill:** marketing:performance-report
   Cambio: añadir caso "investigación caída métrica" como sección
   Prioridad: Media

🔵 EDUCATE (0)
⚪ NOT-WORTH (1): "screenshot del banner roto" — caso único.
```

---

## Reglas de la skill (anti-patrones a evitar)

| ❌ Mal | ✅ Bien |
|--------|---------|
| Proponer skill por TODO lo que se hizo en la sesión | Solo lo que se va a repetir 3+ veces |
| Inventar nombres genéricos ("data-helper-skill") | Nombres descriptivos, kebab-case, dominio incluido |
| Saltar fase 2 (cross-check existentes) | Verificación obligatoria con `skill_search` antes de proponer NEW |
| Proponer skill cuando ya existe `anthropic-skills:X` que aplica | Si la genérica aplica, EDUCATE no NEW |
| Dar prioridad Alta a todo | Solo Alta si frecuencia ≥ 2-3/mes Y tiempo ahorrado ≥ 30 min/uso |
| Output sin evidence ("creo que sería útil") | Cada propuesta cita quote/acción específica de la conversación |
| Proponer skills sin path concreto | Path completo + dominio razonado |

---

## Output esperado para el orquestador (Claude/Codex/agente)

Tras invocar esta skill, el modelo debe presentar al usuario:

```
=== SUGGEST-SKILLS RESULT ===

Auditadas N turnos. Encontrados M patterns. Cross-check vs 170+ skills the company completo.

🟢 NEW SKILLS (X): <lista resumida>
🟡 IMPROVE EXISTING (Y): <lista resumida>
🔵 EDUCATE (Z): <lista resumida con owners>
⚪ NOT-WORTH (W): <breve>

¿Apruebas las prioridades Alta para implementación inmediata? (✅/❌/🤔 por cada)
```

Si Diego responde ✅ → Claude crea la skill (usando `anthropic-skills:skill-creator` o brain_write directo según complejidad).
Si ❌ → archiva propuesta con razón.
Si 🤔 → más contexto requerido, no crear aún.

---

## Encaja con el roadmap the company

Esta skill **arranca el Eje 3** del plan brain v2 (`knowledge/platform/strategy/the company-brain-v2-synthesis.md`):

> "Eje 3 — /skillify loop. Meta-skill que observa uso real del equipo y crea skills nuevas. Resuelve el techo Q3 (non-engineers no extienden). Los humanos NO escriben skills. **Usan Claude diario. El sistema captura patterns. /skillify destila. Owner del dominio aprueba (✅/❌ emoji Slack).**"

Diferencia vs visión completa Eje 3:
- **Esta skill (Fase 1):** invocable manual. Diego/empleado dice "suggest skills" → output.
- **Visión completa Eje 3 (Fase 2 futuro):** automated harvester que analiza TODAS las sesiones del equipo nightly + propone via Slack #brain semanal.

Esta skill es el prerequisito para automatizar después.

---

## Cross-references

- Plan brain v2 (donde encaja): `knowledge/platform/strategy/the company-brain-v2-synthesis.md`
- REGLA 11 (Brain+Skills review): `knowledge/platform/rules/brain-skills-review-before-execution.md`
- Skill creator genérica de Anthropic: `anthropic-skills:skill-creator` (úsala cuando ya sabes qué crear; esta skill PROPONE qué)
- Punta de Flecha (patrón meta-skill estructurada): `knowledge/skills/punta-de-flecha/SKILL.md`
- Garry Tan blog post original (inspiración): "The Book That Read Me Back" / "Fat Skills Thin Harness" (mayo 2026)

---

## Cambios

| Fecha | Cambio | Por |
|-------|--------|-----|
| 2026-05-19 | Skill creada tras conversación Diego sobre patrón /skillify de Garry Tan | Claude Code |
