---
name: employee-onboarding
description: "Onboarding the company para the people agent: Slack, Notion, Holded, Shopify y Google Workspace. Checklist Dia 1/Semana 1, buddy y Brain links iniciales."
metadata:
  source: the company-native
  category: hr
  primary_user: people-agent
  owner: people-agent
  cadence: per_new_employee
  tools_needed: google_workspace, slack_send_message, notion_query, holded_query, brain_search, holded_leaves
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# the company Employee Onboarding

## What it does

Onboarding the company-especifico para the people agent. Combina el workflow general de `human-resources:onboarding` con los sistemas reales de the company: Slack, Notion, Holded, Shopify, Google Workspace y Brain. Genera checklist de pre-start, Dia 1, Semana 1, buddy, links iniciales y seguimiento en Notion.

## When to activate

- Diego o the people agent comunican nuevo empleado con start date.
- HR necesita preparar altas, accesos y contexto antes del primer dia.
- Manager pide checklist adaptado a rol.

## Inputs requeridos

- Nombre completo.
- Email the company.
- Rol.
- Manager.
- Start date.
- Ubicacion: HQ, remote, Mac Mini o VPS.
- Equipo/dominio: CS, retail, finance, digital, merchandising, ops, HR, tech.
- Necesidad de accesos especiales: Shopify staff, Stockagile, Holded, Payhawk, Meta, Klaviyo, Richpanel.

## Stage 1 - Pre-start (T-7d)

1. Pedir laptop y material necesario.
2. Crear/invitar cuentas:
   - Slack invite.
   - Notion seat.
   - Holded employee.
   - Shopify staff si rol retail/ops/ecommerce lo requiere.
   - Google Workspace user con DWD si aplica.
3. Revisar festivos/ausencias del manager con `holded_leaves`.
4. Crear checklist en Notion y linkarlo al manager.
5. Confirmar que cada acceso tenga owner responsable, no solo "pendiente IT".

## Stage 2 - Dia 1

1. Crear welcome doc en Google Drive desde template.
2. Asignar buddy del equipo.
3. Enviar DM Slack al empleado y manager con agenda del dia.
4. Incluir Brain links iniciales:
   - `LAAGAM_CORE`
   - `prompt-maestro-claude.md`
   - `role-boundaries`
   - context-doc de su dominio
5. Confirmar acceso a Slack, Notion, Google Workspace y herramienta primaria del rol.

## Stage 3 - Semana 1

1. Programar meetings con manager, buddy y cross-team key contacts.
2. Instalar Claude Desktop si el rol usara AI agents.
3. Setup 1-click MCP:

```bash
curl your-mcp-endpoint.example/setup.sh | bash
```

4. Pegar prompt maestro y validar que el empleado entiende limites de uso.
5. Para roles CS o customer-facing, revisar AI Act compliance y policy de respuestas.

## Stage 4 - Feedback loop dia 7

the people agent envia DM al empleado y manager:

- Que esta claro.
- Que acceso falta.
- Que decision o contexto bloqueo la primera semana.
- Si el buddy esta funcionando.

Registrar acciones en Notion.

## Stage 5 - Track progress en Notion

Usa `notion_query` para crear o actualizar la pagina de onboarding:

- Status por etapa.
- Owner de cada acceso.
- Fechas objetivo.
- Bloqueos.
- Links a docs y Brain paths.
- Feedback dia 7.

## Anti-patrones

- No saltarse buddy.
- No usar onboarding generico: adaptar por rol y manager.
- No dar Shopify/Holded/Payhawk si el rol no lo requiere.
- No descuidar AI Act compliance si el rol incluye CS o customer-facing.
- No decir "no tengo acceso" sin intentar `google_workspace`, `notion_query` o `holded_query`.

## Tools

- `google_workspace`
- `slack_send_message`
- `notion_query`
- `holded_query`
- `brain_search`
- `holded_leaves`

## Cadencia

Por nuevo empleado. Historico esperado: 1-2/mes.
