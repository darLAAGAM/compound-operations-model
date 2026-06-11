---
name: omnichannel-growth-loop
description: Closed-loop growth methodology for the company (DTC fashion, €5-10M, 2 own stores + the department-store corners corners + online + wholesale). Diagnoses ICP from real Shopify/GA4/Klaviyo data, maps cross-channel halo effects (digital ↔ physical), and outputs 3 concrete actions with owner + KPI. Built to replace generic B2B SaaS growth frameworks that ignore retail spillover.
metadata:
  source: the company-native
  inspired_by: omarismail.com/projects/growth-engine (B2B SaaS, intentionally inverted for DTC)
  category: marketing
  primary_user: marketing-agent
  tools_needed: shopify_query, ga4_query, meta_ads_query, klaviyo_query, tc_analytics_query, brain_search
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# the company Omnichannel Growth Loop

## What it does

Replaces "Meta-only" or "online-only" growth thinking with a **closed loop that treats retail (Store A, Store B, the department-store corners corners) as a force multiplier of digital paid acquisition**, not as a separate silo. Run this skill when the question is "where is our next €1M of growth?" and the answer needs to be data-grounded, not a slide deck.

## When to activate

- ROAS de Meta cae pero revenue Shopify aguanta → hay halo effect no medido
- Apertura de tienda nueva en negociación (Bilbao, Valencia, Amsterdam) → modelar spillover
- the marketing agent pide channel mix anual / quarterly
- the strategy hub prepara weekly P&L y necesita atribución real cross-channel
- Diego dice "vamos a probar TikTok ads / cold outreach / nuevo mercado" → primero pasar por este loop
- Equipo discute si invertir en Pinterest vs Meta vs branded SEO

## Why NOT a B2B SaaS growth framework

Frameworks tipo Omar Ismail Growth Engine, Reforge B2B Loops, etc. asumen:

- Sales-led funnel (Lead → Meeting → Trial → Opportunity → Customer)
- Enrichment B2B (Apollo, Clay, RB2B)
- Cold outreach (HeyReach, Instantly)
- Single channel attribution

**the company es B2C DTC fashion**. Funnel real:

- View → ATC → Checkout → Customer → Repeat (digital)
- Walk-in → Try-on → Purchase → Loyalty (retail)
- **Cross**: Digital ad → branded search → retail walk-in (halo, casi nunca medido)

Si copias el growth engine B2B tal cual, asignas mal el budget durante 6 meses.

## Stage 1 — ICP REAL desde data (no buyer personas inventadas)

**Objetivo**: identificar 3-5 archetipos de cliente con peso real en revenue, no aspiracionales.

### Inputs (que el agente debe pull al activar)

```python
# Cohorts últimos 12 meses
shopify_query("orders.json?status=any&created_at_min=<12mo_ago>&limit=250&fields=id,total_price,customer,line_items,source_name,created_at")

# Customer aggregation
shopify_query("customers.json?limit=250&fields=id,total_spent,orders_count,first_name,addresses,tags")

# Online sessions por device/source
ga4_query("propertyId=..., metrics=sessions,conversions,revenue, dimensions=deviceCategory,source,medium,city, dateRanges=last_365d")

# Foot traffic por tienda
tc_analytics_query("store=store_a,store_b, date_range=last_365d")
```

### Análisis a producir

Segmentar por **estos 4 axes simultáneamente** (no por uno solo):

1. **Spend tier**: <€200, €200-€800, €800-€2K, >€2K LTV
2. **Frequency**: 1 order, 2-3, 4-6, 7+
3. **Channel mix**: 100% online | mixed | 100% retail (POS) | 100% wholesale
4. **Geography**: Madrid metro, Barcelona metro, resto España, EU, USA, RoW

### Output esperado

Tabla con **5 archetipos** ordenados por contribución a revenue total:

```
| Archetype | % revenue | LTV avg | Channel mix | Geo | Insight accionable |
|---|---|---|---|---|---|
| "Madrid loyalist" | 28% | €1.4K | 70% retail 30% online | Madrid metro | Retail walk-in es el trigger; Meta debe ser branded |
| "Barcelona discovery" | 14% | €380 | 90% online | Barcelona metro | Aún no convertimos a retail; abrir Store B v2? |
| ... | ... | ... | ... | ... | ... |
```

**Anti-patrón**: NO segmentar solo por "edad/género/intereses" como hace Meta. Eso es Meta tier-1 segmentation, no ICP real.

## Stage 2 — Channel attribution + halo loop mapping

**Objetivo**: detectar dónde dejas dinero porque el modelo de atribución last-click subestima el efecto cruzado.

### Diagnósticos a correr (en este orden)

#### 2.1 — Discrepancia attribution

```python
# Revenue verdadero (source of truth)
shopify_revenue = shopify_query("orders.json...total_price sum")

# Revenue atribuido por Meta
meta_attributed = meta_ads_query("act_<id>/insights?fields=action_values,purchase_roas")

# Revenue atribuido por GA4
ga4_attributed = ga4_query("metrics=purchaseRevenue,transactions,sessionDefaultChannelGroup")

# Gap = shopify_revenue - sum(canales_atribuidos)
# Si gap > 15%, hay halo no capturado
```

Si Meta dice ROAS 6.05x pero Shopify total revenue / total Meta spend = 12x → tienes halo masivo. Si es al revés, tienes attribution overlap o fraude.

#### 2.2 — Branded search lift

```python
gsc_search_analytics(query="the company OR brand_terms", dimensions=date)
# Correlación con: Meta spend daily, retail openings, PR mentions
```

Si Meta spend ↑ 30% y branded search ↑ 20% (con 7-14d lag), tu Meta está haciendo trabajo de awareness aunque ROAS direct no lo refleje.

#### 2.3 — Retail spillover de digital

```python
# Para Store A + Store B:
tc_analytics_query("foot_traffic daily, last_180d")
# Cruzar con:
#  - Meta spend en geo Madrid / Barcelona
#  - GA4 sessions en city=Madrid
#  - Branded search Madrid

# Si correlación foot_traffic ~ meta_spend_geo > 0.4, tiendas son halo de Meta.
```

#### 2.4 — Digital re-engagement de walk-ins

```python
# Customers POS en últimos 90d:
shopify_query("customers donde source_name=pos")
# ¿Están en Klaviyo? ¿Han abierto algún email? ¿Hicieron repeat online?
klaviyo_query("metrics: opened_email, clicked_email, placed_order, segment=pos_customers_90d")
```

Si <40% de walk-ins re-compran online en 90d, el loop está roto en la dirección retail→digital.

### Output esperado

```
| Loop direction | Status | Gap | Fix prioritario |
|---|---|---|---|
| Digital → Retail | ✅ Funciona (corr 0.6) | €180K/año halo no atribuido a Meta | Mover 20% budget Meta de "scaling" a "branded" |
| Retail → Digital | 🔴 Roto | 60% walk-ins no reactivan | Klaviyo POS welcome flow + 90-day winback |
| Branded → Direct | 🟡 OK pero subutilizado | Google Ads SQR captura poco | Aumentar Google branded budget +€2K/mes |
```

## Stage 3 — Loop execution (3 acciones concretas, no roadmap)

**Objetivo**: producir 3 acciones que se pueden ejecutar esta semana, no un plan de 90 días.

### Reglas duras del output

1. **Cada acción tiene owner real** (persona del equipo, no "marketing team")
2. **Cada acción tiene KPI específico** medible en ≤4 semanas
3. **Cada acción tiene tool/playbook** ya existente en el swarm (no inventar)
4. **Total ≤ 3 acciones**. Si quieres proponer 7, has fallado el ejercicio.

### Plantilla

```markdown
## Growth Loop — Acciones [semana X]

### Acción 1 — [verbo + objeto, ≤8 palabras]
- **Owner**: [nombre persona]
- **KPI**: [métrica específica + threshold + plazo]
- **Tool/playbook**: [skill del swarm o sistema concreto]
- **Por qué ahora**: [data del stage 1/2 que la justifica]
- **Riesgo si no hacemos**: [escenario malo medible]

### Acción 2 — ...
### Acción 3 — ...
```

### Ejemplo (output real esperable)

```markdown
### Acción 1 — Activar Klaviyo POS winback 90-day
- Owner: Marta (Klaviyo lead)
- KPI: repeat rate POS customers 60d > 25% (baseline 12%)
- Tool/playbook: skill `email-sequence` + segment `pos_customers_90d_no_repeat`
- Por qué ahora: Stage 2 detecta 60% walk-ins no reactivan en 90d. €120K LTV perdido/año estimado.
- Riesgo si no hacemos: cada apertura nueva amplifica el problema (más walk-ins, mismo gap).

### Acción 2 — Reducir Meta scaling -20% / Aumentar Google branded +€2K/mes
- Owner: the marketing agent
- KPI: branded search impressions +30% en 4 sem; Meta ROAS direct se mantiene ±10%
- Tool/playbook: skills `ads-channel-mix-optimizer` + `ads-ad-spend-allocator`
- Por qué ahora: ROAS Meta 6x pero halo no capturado. Branded subutilizado.
- Riesgo si no hacemos: dejamos €15K/mes en mesa.

### Acción 3 — Modelar Bilbao pre-apertura con Stage 1+2
- Owner: the strategy hub (coord con the retail agent)
- KPI: forecast revenue Bilbao tienda mes 1-12 con confianza ±25%
- Tool/playbook: skills `ads-budget-scenario-planner` + `ads-roas-forecasting` + brain `<brain-root>/knowledge/retail/`
- Por qué ahora: decisión local-pick antes de firmar lease.
- Riesgo si no hacemos: abrir tienda sin modelar = €200-500K riesgo.
```

## Anti-patrones (qué NO hacer)

- ❌ Tratar tiendas como "drag" o "necesidad operativa". Son **force multiplier** del digital.
- ❌ Medir paid ROAS solo en last-click web. Mata el halo.
- ❌ Importar funnel B2B (Lead/MQL/SQL/Trial). the company no tiene SDRs ni sales reps.
- ❌ Cold outreach LinkedIn / Instantly. **No es un canal en fashion B2C** salvo wholesale.
- ❌ ICP basado en "intereses Meta" sin cruzar con Shopify LTV.
- ❌ Activar Pinterest / TikTok / nuevo canal sin pasar Stage 1+2 antes.
- ❌ Output de 15 bullets sin owner. Significa "ningún acción ejecutable".

## Cadencia recomendada

- **Stage 1 (ICP)**: refresh trimestral
- **Stage 2 (Attribution)**: monthly review (correr al final de mes con the strategy hub + the marketing agent)
- **Stage 3 (Actions)**: cada lunes, hasta 3 acciones rotativas

## Referencias en el brain

- `<brain-root>/knowledge/strategy/the company-bp-interno-2026.md` — revenue targets por canal
- `<brain-root>/knowledge/marketing/meta-ads-q1-2026-analysis.md` — baseline Meta performance
- `<brain-root>/knowledge/retail/metrics-insights.md` — KPIs físicos Store A + Store B
- `<brain-root>/knowledge/marketing/brand-guidelines-2026.md` — posicionamiento ya definido (no re-inventar)
