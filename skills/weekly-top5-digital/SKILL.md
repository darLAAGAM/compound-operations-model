---
name: weekly-top5-digital
description: "Genera el Weekly TOP 5 Digital report de the company en formato the digital lead. Pull Shopify + GA4 + Meta + Klaviyo, top 5 SKUs, insights y draft listo lunes 9am."
metadata:
  source: the company-native
  category: ads_reporting
  primary_user: marketing-agent
  owner: digital-lead
  cadence: weekly_sunday_2200_cet
  tools_needed: shopify_query, ga4_query, meta_ads_query, klaviyo_query, brain_search, slack_send_message
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Weekly TOP 5 Digital Generator

## What it does

Genera el reporte semanal TOP 5 Digital de the company replicando el formato de the digital lead. Usa como referencias Brain:

- `knowledge/the company/marketing/weekly-top5-2026-W09.md`
- `knowledge/the company/marketing/weekly-top5-digital-w7-2026.md`

El reporte debe explicar que productos lideran, que cambia WoW, que canales sostienen el revenue y que acciones deberian tomar Digital, Merchandising y Ecommerce.

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

- Cron domingo 22:00 CET con semana cerrada.
- the digital lead lo invoca manualmente si necesita un draft antes del lunes 9:00.
- the marketing agent lo usa cuando necesita contexto semanal de channel mix y producto.

## Stage 1 - Pull data semana cerrada

1. Define la semana cerrada anterior en timezone Europe/Madrid.
2. `shopify_query`: pide agregacion por producto/SKU si la tool lo soporta: `group_by=sku`, `metrics=net_revenue,units,orders,discounts,refunds`, `date_range=closed_week`, `limit=50`, `fields=sku,product_title,variant_title,net_revenue,units,orders,refunds,discounts,country,channel`. Si no hay agregacion, trae solo top 50 orders por revenue con esos campos, resume por SKU y descarta raw.
3. Resume Shopify en <=300 tokens: top SKUs, revenue total, units total, refunds/discounts relevantes. Descarta raw antes de seguir.
4. `ga4_query`: pide solo metricas sumario de semana cerrada y semana previa: `sessions,users,conversions,totalRevenue,conversionRate,averageOrderValue` por `defaultChannelGroup` y opcional `country`; no pidas eventos raw ni landing pages salvo que falte explicacion.
5. Resume GA4 en <=300 tokens y descarta raw.
6. `meta_ads_query`: pide solo sumario por campaign/adset con `fields=campaign_name,adset_name,spend,purchases,purchase_value,roas,cpm,ctr,cpa`, `limit=50`, semana cerrada y semana previa. No traigas ads creativos ni breakdowns raw.
7. Resume Meta en <=300 tokens y descarta raw.
8. `klaviyo_query`: pide sumario de attributed revenue, flows y campaigns con `fields=name,type,attributed_revenue,sends,opens,clicks,placed_order`, `limit=50`, semana cerrada y semana previa. No traigas eventos/perfiles raw.
9. Resume Klaviyo en <=300 tokens y descarta raw.
10. Para WoW, usa agregados de semana previa. Solo consulta trailing 4 semanas si falta contexto para un top SKU o hay una anomalia relevante.

## Stage 2 - Identificar top 5 productos

Ranking base:

- 50% revenue neto.
- 25% unidades vendidas.
- 15% WoW change en unidades/revenue.
- 10% cross-market signals: aparece en varios paises, canales o cohorts.

Output minimo por SKU: nombre producto, SKU, unidades, revenue, stock si esta disponible, WoW, mercados clave, status SS26/carryover/restock/BIS/OOS si se puede inferir.

Si necesitas stock para los top 5, consulta solo esos 5 SKUs con campos `sku,available_stock,reserved_stock,warehouse,status`; no consultes catalogo completo.

## Stage 3 - Channel mix analisis

Calcula:

- % revenue por canal: Shopify online, POS si aparece, Meta, Klaviyo, organic/search/direct/referral segun GA4.
- WoW por canal: revenue, sessions, conversion rate, AOV, spend, ROAS.
- Divergencias: Shopify revenue sube pero paid attributed cae, Klaviyo sube por flow puntual, GA4 sessions caen pero conversion mejora.

No fuerces precision de attribution si las fuentes no cuadran. Declara el gap y separa "observado" de "inferido".

## Stage 4 - Write report en tono the company

Usa estructura directa, numerica y accionable como los reports del Brain. Antes de redactar, busca `brand-cog` y las brand guidelines con `brain_search` si el tono o naming genera dudas.

Evita copy generico. El estilo correcto es: producto + cifra + cambio + implicacion. Ejemplo: "NAELIA domina en 4 de 5 paises; no es solo promo, es cross-market fit."

## Output esperado

Markdown con estas secciones:

- `[TOP 5 SKUs]`: cantidad, revenue y notas WoW.
- `[Channel mix]`: tabla corta por canal con revenue/spend/ROAS o metricas disponibles.
- `[Insights accionables]`: maximo 3, cada uno con owner sugerido.
- `[Riesgos]`: stockout, returns, dependencia de descuento, canal cayendo o attribution gap.
- `[Slack-friendly summary]`: 5-8 lineas listas para pegar en Slack.

## Tools

- `shopify_query`
- `ga4_query`
- `meta_ads_query`
- `klaviyo_query`
- `brain_search`
- `slack_send_message`

## Cadencia

Weekly, domingo 22:00 CET. Draft listo para review lunes 9:00.
