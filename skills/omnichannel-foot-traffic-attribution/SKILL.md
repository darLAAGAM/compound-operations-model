---
name: omnichannel-foot-traffic-attribution
description: "Cruza foot traffic Store A/Store B con Meta geo spend, GA4 city sessions y Shopify POS. Estima halo effect por tienda y recomienda redistribucion spend."
metadata:
  source: the company-native
  category: ads_diagnostics
  secondary_category: marketing
  primary_user: marketing-agent
  owner: strategy-hub
  cadence: monthly_day_1_0900_cet
  tools_needed: tc_analytics_query, meta_ads_query, ga4_query, shopify_query, gsc_search_analytics, brain_search, slack_send_message
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Omnichannel Foot Traffic Attribution

## What it does

Implementa Stage 2.3 de `the company-omnichannel-growth-loop` como playbook mensual. Cruza foot traffic diario de Store A/Store B con Meta Ads geo spend, GA4 city sessions, GSC branded search y Shopify POS revenue para estimar halo effect por tienda y recomendar redistribucion de spend entre Madrid, Barcelona y futuras aperturas.

## ⚡ Query economy (CRÍTICO — leer antes de ejecutar)

Este skill se ejecuta en un agente con context window limitado. Para NO agotarlo:

1. **Una query a la vez**: ejecuta una query, RESUME su resultado en ≤300 tokens (los números que importan), DESCARTA el raw, y solo entonces pasa a la siguiente query. Nunca encadenes 5 queries antes de procesar.
2. **Campos específicos siempre**: usa `fields=...` para traer solo las columnas necesarias. Nunca pidas el objeto completo.
3. **Límites pequeños**: `limit=50` máximo por query. Si necesitas más, agrega/cuenta server-side o pagina explícitamente solo si es imprescindible.
4. **Date ranges acotados**: pide la ventana mínima necesaria (ej. 7d, no 90d, salvo que el stage lo requiera).
5. **Agrega antes de traer**: cuando la tool soporte agregación/count, úsala en vez de traer rows y sumar en el agente.
6. **Si el output va a ser largo**: produce el resultado en secciones cortas, no acumules todo en memoria hasta el final.

Si en mitad de la ejecución el context se siente lleno, ENTREGA lo que tengas con una nota "[parcial: faltó stage N por límite de context]" en vez de fallar en silencio.

## When to activate

- Cron mensual dia 1 a las 9:00 CET.
- Manual antes de una decision de apertura de tienda.
- Cuando Meta ROAS parece caer pero retail/POS o branded search suben.

## Stage 1 - Pull foot traffic daily

Usa `tc_analytics_query` para el rango minimo necesario: por defecto ultimos 30 dias + periodo comparable anterior. Solo usa 180 dias si el caller pide analisis mensual historico o apertura. TC Analytics es scraping lento (~60s), asi que ejecuta 1 tienda a la vez:

1. `store=store_a`, `date_range=needed_range`, `fields=date,exterior_traffic,entries,attraction_rate,tickets,conversion_rate,revenue,dwell_time`.
2. Resume Store A en <=300 tokens y descarta raw.
3. `store=cubi`, mismos campos.
4. Resume Store B en <=300 tokens y descarta raw.

Extrae por dia: exterior traffic, entries, attraction rate, tickets, conversion rate, revenue y dwell time si esta disponible.

## Stage 2 - Pull Meta Ads spend daily por geo

Usa `meta_ads_query` con breakdown geografico para Madrid y Barcelona:

- spend diario
- impressions
- reach
- clicks
- purchases/value si esta disponible
- campaign/adset naming para detectar activaciones locales

Usa `limit=50`, `fields=date,region,city,campaign_name,adset_name,spend,impressions,reach,clicks,purchases,purchase_value`, mismo rango que Stage 1 y resumen por ciudad/campaign antes de seguir. No mezcles spend nacional con geo spend si el breakdown no permite asignacion razonable.

## Stage 3 - Pull GA4 sessions por city

Usa `ga4_query` para el mismo rango acotado de Stage 1:

- city: Madrid, Barcelona y otras ciudades relevantes.
- sessions, users, conversions, revenue, default channel group, source/medium.
- branded vs non-branded si la configuracion lo permite; si no, complementa con GSC.

Pide agregacion diaria por city con `fields=date,city,defaultChannelGroup,sessions,users,conversions,totalRevenue` y `limit=50`. Resume y descarta raw antes de Stage 4.

## Stage 4 - Pull Shopify POS revenue por location

Usa `shopify_query` para POS revenue y orders por location:

- Store A
- Store B
- the department-store corners corners si aparecen

Pide agregacion por dia/location con `fields=date,location_name,sales_channel,orders,net_revenue,refunds`, `limit=50`, mismo rango que Stage 1. Separa POS, online y refunds. Mantener timezone consistente Europe/Madrid. Resume y descarta raw.

## Stage 5 - Calcular correlaciones

Calcula correlaciones y lags:

- foot_traffic vs meta_spend_geo con lags 0, 1, 3, 7 y 14 dias.
- POS revenue vs meta_spend_geo.
- GA4 city sessions vs foot_traffic.
- branded search lift (`gsc_search_analytics`) vs meta_spend_geo.

Para `gsc_search_analytics`, pide solo branded query summary por city/country si esta disponible, `fields=date,query,clicks,impressions,ctr,position`, `limit=50`, mismo rango. Resume antes de correlacionar.

Output debe separar:

- correlacion observada
- posible causalidad
- confounders: weather, holidays, drops, sales, store events, stockouts, PR
- confianza: alta/media/baja

## Stage 6 - Output halo effect + spend recommendation

Tabla por tienda:

- store
- city
- foot traffic delta
- POS revenue delta
- Meta spend geo
- GA4 sessions city
- branded search lift
- estimated halo effect
- recommended spend action
- confidence

La recomendacion debe decir cuanto mover, desde donde hacia donde, durante que periodo y que KPI observar.

## Stage 7 - Input para nuevas aperturas

Para Bilbao o Valencia:

1. Usa benchmarks Madrid/Barcelona.
2. Modela spillover esperado con rango conservador/base/upside.
3. Explicita supuestos: poblacion objetivo, current online demand, branded search baseline, store catchment, paid media support.
4. Si la decision implica >EUR50K o es irreversible, elevar a `punta_de_flecha` antes de recomendar.

## Tools

- `tc_analytics_query`
- `meta_ads_query`
- `ga4_query`
- `shopify_query`
- `gsc_search_analytics`
- `brain_search`
- `slack_send_message`

## Cadencia

Mensual, dia 1 a las 9:00 CET.
