> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._

# Swarm Propagation — Rollout de cualquier cambio a todos los nodos del swarm

*Creado: 19 mayo 2026 — Diego Arroyo*
*Inspirado en: rollouts repetidos (Mobbin, prompt maestro v1.6/1.7/1.8, REGLA 10/11) donde reinventaba mapa de nodos cada vez*
*Encaja con: REGLA 11 (Brain+Skills review) + sync script `<your-services-dir>/prompt-sync/sync.py`*

---

## Qué es

Skill operativo que **propaga un cambio (MCP, regla, prompt, credencial, doc canonical) a TODOS los nodos del swarm the company** en orden correcto, sin olvidar ningún site, con verificación post-rollout.

**Objetivo:** eliminar el anti-pattern "propagué a 4 sitios pero olvidé el 5º → divergencia silenciosa entre agentes".

---

## Cuándo invocar

| Situación | Trigger |
|-----------|---------|
| Añadir MCP nuevo (HTTP o stdio) al swarm | "propaga `<MCP>` a todos los nodos" |
| Bump prompt maestro a nueva versión | "actualiza prompt maestro a vX.Y en todos los nodos" |
| Añadir REGLA obligatoria nueva | "rollout REGLA X a todo el swarm" |
| Compartir credencial/token nuevo | "propaga `$NEW_TOKEN` a VPS + Mac Mini + agentes" |
| Distribuir skill canonical | "asegúrate que skill `X` está en todos los nodos" |
| Cambio en COMPANY_CORE.md de algún agente | "sync workspace de `<agente>` con canonical brain" |

**Anti-pattern:** usar para cambios one-off que solo afectan a UN nodo (no es propagación, es edición local).

---

## Mapa canonical de nodos del swarm (snapshot 2026-05-19)

| # | Nodo | Tipo | Path config | Path prompt/regla | Acceso |
|---|------|------|-------------|-------------------|--------|
| 1 | **Claude Code Diego** (Mac local) | Cliente humano | `/Users/diegoarroyo/.claude.json` | `/Users/diegoarroyo/.claude/CLAUDE.md` | Edit local |
| 2 | **Codex CLI Diego** (Mac local) | Cliente humano | `/Users/diegoarroyo/.codex/config.toml` | `/Users/diegoarroyo/.codex/AGENTS.md` | Edit local |
| 3 | **Claude Desktop equipo** (todo el equipo) | Cliente humano | n/a (gestionado via setup.sh) | Setting → Personal Preferences → pegar prompt maestro | `setup.sh` en `<your-mcp-server-dir>/` |
| 4 | **the strategy hub** (VPS Hetzner) | Agente OpenClaw | `/root/.openclaw/openclaw.json` | `/root/.openclaw/workspace-main/COMPANY_CORE.md` | `ssh <agent>@<your-host>` |
| 5 | **the CS agent** (Mac Mini) | Agente OpenClaw | `/Users/<agent>/.openclaw/openclaw.json` | `/Users/<agent>/.openclaw/workspace-<agent>/COMPANY_CORE.md` | `ssh <agent>@<your-host>` (vía VPS jump) |
| 6 | **the finance agent** (VPS workspace) | Agente OpenClaw | hereda openclaw.json VPS | `/root/.openclaw/workspace-<agent>/COMPANY_CORE.md` | `ssh <agent>@<your-host>` |
| 7 | **the retail agent** (VPS workspace) | Agente OpenClaw | hereda openclaw.json VPS | `/root/.openclaw/workspace-<agent>/COMPANY_CORE.md` | idem |
| 8 | **the marketing agent** (VPS workspace) | Agente OpenClaw | hereda openclaw.json VPS | `/root/.openclaw/workspace-<agent>/COMPANY_CORE.md` | idem |
| 9 | **the merchandising agent** (VPS workspace) | Agente OpenClaw | hereda openclaw.json VPS | `/root/.openclaw/workspace-<agent>/COMPANY_CORE.md` | idem |
| 10 | **the people agent** (Mac Mini) | Agente OpenClaw | `/Users/<agent>/...` (pendiente confirmar) | pendiente | Mac Mini, fuera de sync.py actual |

⚠️ **Gotcha conocida (12-may-2026):** the finance agent/the retail agent/the marketing agent/the merchandising agent tienen además `/Users/Shared/agents-config/agents/<agent>/openclaw.json` que un maintenance script sobreescribe. Si propagas MCP a esos agentes y ves que se revierte → ese script es la fuente del problema. Pendiente arreglar el script.

---

## Tabla por tipo de cambio: qué tocar dónde

### A) MCP nuevo (HTTP con OAuth, e.g. Mobbin)

| Nodo | Archivo | Bloque a añadir |
|------|---------|-----------------|
| Claude Code Diego | `~/.claude.json` | `mcpServers.<name>` con `mcp-remote` |
| Codex CLI Diego | `~/.codex/config.toml` | `[mcp_servers.<name>]` con `command = "/opt/homebrew/bin/mcp-remote"` |
| Claude Desktop equipo | `setup.sh` línea config.mcpServers | añadir bloque mcp-remote |
| the strategy hub + 5 VPS | `/root/.openclaw/openclaw.json` | `mcp.servers.<name>` formato stdio (mcp-remote) |
| the CS agent Mac Mini | `/Users/<agent>/.openclaw/openclaw.json` | idem stdio |
| OAuth tokens | `~/.mcp-auth/mcp-remote-0.1.37/{hash}_tokens.json` | Diego OAuth una vez en Codex CLI → `scp` a VPS + Mac Mini (ver skill `oauth-token-share`) |

### B) MCP nuevo (stdio local, e.g. yahoo-finance)

Solo afecta a clientes que lo necesiten. NO propagar al swarm de agentes por defecto — pregunta al usuario si quiere también ahí.

### C) Prompt maestro nueva versión (v1.X → v1.Y)

| Nodo | Archivo | Acción |
|------|---------|--------|
| Canonical brain | `knowledge/platform/onboarding/prompt-maestro-claude.md` | `brain_write` con v1.Y completa + histórico |
| Claude Code Diego | `~/.claude/CLAUDE.md` | Edit sección correspondiente o regla nueva |
| Codex CLI Diego | `~/.codex/AGENTS.md` | Edit sección equivalente |
| 6 workspaces VPS | `/root/.openclaw/workspace-*/COMPANY_CORE.md` | **Ejecutar `python3 <your-services-dir>/prompt-sync/sync.py`** (automático) |
| Claude Desktop equipo | setup.sh + Notion onboarding page `33e09b39ff3181098c0cd1dd76f1f1c9` | Update página + reshare URL |
| Mac Mini agents (the people agent) | pendiente | Manual ssh hasta extender sync.py |

### D) Regla obligatoria nueva (REGLA X)

1. Crear doc canonical: `knowledge/platform/rules/<regla-slug>.md`
2. Añadir bloque REGLA X al prompt maestro canonical → bumpear versión
3. Disparar tipo C (prompt maestro nueva versión)

### E) Credencial nueva (token, API key)

| Nodo | Archivo | Notas |
|------|---------|-------|
| Mac local Diego | `~/.zshrc` o `~/.config/the company/env` | `export $NEW_TOKEN=...` |
| VPS | `/root/.bashrc` o `/etc/the company/env` | idem + reload servicios systemd que lo usen |
| MCP server `.env` | `<your-mcp-server-dir>/.env` | si la tool MCP lo necesita |
| Agentes OpenClaw | nada extra (heredan env del VPS) | reload OpenClaw gateway tras update env |

⚠️ NO commitear credenciales al brain. Solo nombre de variable, nunca el valor.

### F) Skill canonical nueva

1. `brain_write knowledge/skills/<slug>/SKILL.md` (esto es el master)
2. Skill se sirve via `skill_read` MCP tool — los nodos lo leen on-demand
3. **NO** copiar SKILL.md a cada nodo. Brain compartido es la fuente.
4. Verificar discoverable: `skill_search("<keyword del skill>")` → debe devolver el nuevo

---

## Protocolo de ejecución (5 fases, ~15-30 min según scope)

### Fase 0 — Pre-flight (~2 min)

```python
# 1. Confirmar qué tipo de cambio es (A/B/C/D/E/F arriba)
# 2. brain_search("<dominio del cambio>") — ver si hay rollout previo similar
# 3. Si MCP nuevo con OAuth: verificar que Diego ya autorizó OAuth en SU Codex CLI primero
#    (Codex CLI usa mcp-remote → genera tokens en ~/.mcp-auth/ que después se propagan)
```

### Fase 1 — Update canonical brain (~3 min)

Siempre **brain primero**, propagación después. Sin esto, los agentes pueden auto-sincronizar pero leen versión vieja.

```python
brain_write("<path canonical>", new_content)
# Ej: knowledge/platform/rules/<nueva-regla>.md
# Ej: knowledge/platform/onboarding/prompt-maestro-claude.md (bumpeada)
```

### Fase 2 — Propagar a clientes Diego (~5 min)

- Edit `/Users/diegoarroyo/.claude/CLAUDE.md` (sección apropiada)
- Edit `/Users/diegoarroyo/.codex/AGENTS.md` (sección equivalente)
- Si MCP: editar `~/.claude.json` + `~/.codex/config.toml`

### Fase 3 — Propagar a agentes (~5 min)

**Caso A (prompt maestro):**
```bash
python3 <your-services-dir>/prompt-sync/sync.py
# Output esperado: "6 written, 0 unchanged, 0 skipped"
```

**Caso B (MCP/config OpenClaw):**
```bash
# VPS the strategy hub
ssh <agent>@<your-host> 'cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.bak-$(date +%s)'
# Editar JSON con jq o python in-place, añadir mcp.servers.<name>
# Validar JSON: python3 -c "import json; json.load(open('/root/.openclaw/openclaw.json'))"

# Mac Mini the CS agent (vía VPS jump)
ssh <agent>@<your-host> 'ssh <agent>@<your-host> "cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak-$(date +%s)"'
# idem edit + validate
```

**Caso E (credencial):**
- Update env files + reload servicios systemd: `systemctl restart the company-mcp` (si aplica)

### Fase 4 — Propagar a Claude Desktop equipo (~3 min)

Si el cambio afecta al prompt maestro o nuevo MCP que el equipo usa:

1. Update `setup.sh` en `<your-mcp-server-dir>/setup.sh` (sección mcpServers)
2. Si es prompt maestro: update Notion onboarding page (`33e09b39ff3181098c0cd1dd76f1f1c9`) → equipo lo ve y recopia
3. Anunciar en Slack #ai-ops si es REGLA nueva obligatoria

### Fase 5 — Verificación post-rollout (~5 min)

Por tipo de cambio:

| Tipo | Verificación |
|------|--------------|
| MCP nuevo | `agent_send(<agent>, "lista tus tools disponibles, ¿ves <new_tool>?")` → debe responder sí |
| Prompt maestro | `grep "version: 1.Y" /root/.openclaw/workspace-*/COMPANY_CORE.md` → todos los workspaces |
| REGLA nueva | `agent_send(<agent>, "qué reglas obligatorias tienes activas")` → debe mencionar nueva |
| Credencial | servicio que la usa hace request real con éxito |
| Skill | `skill_search("<keyword>")` desde MCP → devuelve nuevo skill |

Si verificación falla → reset desde backup `.bak-<timestamp>` y diagnosticar antes de re-aplicar.

---

## Checklist rápido para invocar

```
□ Fase 0 — Confirmé tipo de cambio (A/B/C/D/E/F)
□ Fase 1 — brain canonical actualizado primero
□ Fase 2 — CLAUDE.md + AGENTS.md Diego actualizados
□ Fase 3 — agentes propagados (sync.py o manual)
□ Fase 4 — equipo Claude Desktop si aplica (setup.sh + Notion)
□ Fase 5 — verificación post-rollout con agent_send / grep / skill_search
□ Memory entry: brain_write a memory/YYYY-MM-DD-<cambio>.md
□ Si propagué REGLA: doc canonical creada en knowledge/platform/rules/
```

---

## Ejemplo real (uso esperado de esta skill)

### Input

```
Diego: añade el MCP de Linear (https://mcp.linear.app/mcp) a todos los nodos
```

### Output esperado tras invocar swarm-propagation

```
## Plan de rollout MCP Linear

**Tipo:** A — MCP HTTP con OAuth

**Fase 0:** confirmado. Diego debe hacer OAuth Linear en SU Codex CLI primero.
  Ejecuta: `codex mcp add linear --transport http https://mcp.linear.app/mcp`
  Después invoca el OAuth y avísame.

**Fase 1:** No aplica (no es prompt maestro ni regla, no hay canonical doc nuevo).

**Fase 2:** Edit `~/.claude.json` + `~/.codex/config.toml` Diego — añadir bloque Linear.

**Fase 3:** ssh VPS + the CS agent — editar openclaw.json con `mcp.servers.linear` (mcp-remote stdio).

**Fase 4:** Update setup.sh para Claude Desktop equipo.

**Fase 5:**
  - `agent_send(<agent>, "¿ves mcp__linear__*?")` debe responder sí
  - Memory entry: `memory/2026-05-19-linear-mcp-rollout.md`

**ETA total:** ~25 min. Dependencia bloqueante: OAuth Diego (paso 0).

¿Procedo?
```

---

## Anti-patterns (lo que ROMPE el rollout)

| ❌ Mal | ✅ Bien |
|--------|---------|
| Editar agentes antes del brain canonical | Brain primero. Si no, agentes auto-sincronizan versión vieja en próxima sesión |
| Olvidar `setup.sh` para Claude Desktop equipo | El equipo no recibe el cambio nunca |
| Skip backup `.bak-<ts>` antes de editar config | Si rompes JSON, no hay rollback rápido |
| Propagar MCP a the finance agent/the retail agent/the marketing agent/the merchandising agent sin avisar de maintenance script | Cambio se revierte en próxima ejecución del script |
| Verificar solo "se escribió el archivo" | No verifica funcionalidad. Hay que pedir al agente que use la tool |
| No documentar en memory entry | Próximo rollout reinventas el mapa |
| Hacer rollout en horario activo del equipo sin avisar | Si setup.sh cambia, próximo `npx setup` del equipo trae cosas inesperadas |

---

## Cross-references

- Role boundaries (Claude orquesta esto, no Codex): `knowledge/platform/agents/role-boundaries.md`
- Sync script prompt master: `<your-services-dir>/prompt-sync/sync.py`
- OAuth token sharing (sub-skill para tipo A): `knowledge/skills/oauth-token-share/SKILL.md` *(pending)*
- Rollout Mobbin precedente (ejemplo trabajado): `memory/2026-05-12-mobbin-mcp-rollout-swarm.md`
- Mapa nodos en prompt maestro: `knowledge/platform/onboarding/prompt-maestro-claude.md` (sección "Aplicación por contexto")
- REGLA 11 (Brain+Skills review): `knowledge/platform/rules/brain-skills-review-before-execution.md`

---

## Cambios

| Fecha | Cambio | Por |
|-------|--------|-----|
| 2026-05-19 | Skill creada tras 4 rollouts repetidos (Mobbin + prompts v1.6/1.7/1.8). ROI estimado 1h/mes + consistencia entre nodos. | Claude Code |
