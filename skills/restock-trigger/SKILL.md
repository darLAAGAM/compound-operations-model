---
name: restock-trigger
description: "Detecta SKUs the company con alta velocidad de venta + low stock y genera propuesta automatizada de restock con forecast para the merchandising agent + the merch lead."
metadata:
  source: the company-native
  category: merchandising
  primary_user: merchandising-agent
  owner: merch-lead
  cadence: daily_0800_cet
  tools_needed: shopify_query, stockagile_query, brain_search, slack_send_message
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Restock Trigger Agent

## What it does

Detecta SKUs con alta velocidad de venta y stock bajo, calcula WOS por almacen y total, y propone restock con forecast, unidades, lead time esperado y proveedor historico. El objetivo es que the merchandising agent e the merch lead reciban una decision preparada, no una lista cruda de stock.

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

- Cron diario 8:00 CET.
- Manual a demanda antes de buys, restocks, drops o reuniones de merchandising.
- Activar si hay senales de stockout en core SKUs o si un producto acelera WoW.

## Stage 1 - Calcular ROS

1. Usa `shopify_query` para agregacion server-side por SKU de los ultimos 28 dias: `group_by=sku`, `metrics=units,net_revenue,orders`, `date_buckets=7d,14d,28d`, `limit=50`, `fields=sku,product_title,units_7d,units_14d,units_28d,net_revenue_7d,net_revenue_28d,orders_7d,tags`.
2. Excluye cancelaciones, fraud, refunds completos y ventas internas con filtros server-side si estan disponibles; si no, usa solo campos agregados y marca limitacion.
3. Resume top 50 SKUs por velocidad/revenue en <=300 tokens y descarta raw. No consultes line items individuales salvo para 1-2 SKUs ambiguos.
4. Calcula ROS diario y semanal: units/day, units/week, revenue/week.
5. Marca aceleracion si ROS 7d > 1.3x ROS 28d o si revenue WoW crece >25%.
6. Pasa a Stage 2 solo los SKUs que superen el filtro de velocidad/aceleracion o sean core en Brain, maximo 50.

## Stage 2 - Pull stock multi-warehouse

Usa `stockagile_query` solo para los SKUs filtrados en Stage 1, maximo 50, con `fields=sku,product_name,warehouse,available,reserved,in_transit,blocked,status` para stock actual por SKU en:

- Stockabee
- Store B
- Store A
- Amphora
- Amsterdam

Separa stock disponible, reservado, en transito y bloqueado si la API lo devuelve. Resume por SKU/warehouse en <=300 tokens, descarta raw y calcula WOS con stock disponible + stock transferible, no stock bloqueado.

## Stage 3 - Calcular WOS

Formula: `WOS = stock_total_disponible / ROS_semanal`.

Flags:

- `urgent`: WOS < 2.
- `risk`: WOS < 4.
- `watch`: WOS 4-8 si ROS esta acelerando.

Si ROS es cero, no dividas por cero: clasifica como no actionable salvo que el SKU sea core y tenga stock muy bajo.

## Stage 4 - Forecast historico

1. Usa trailing 4 semanas solo para SKUs `urgent` o `risk`, maximo 20. Si Stage 1 ya trajo buckets 7/14/28d, reutilizalos y no repitas query.
2. Si falta granularidad semanal, ejecuta una query adicional por lotes pequenos con `limit=50` y `fields=sku,week,units,net_revenue`.
3. Ajusta por tendencia: media ponderada 40% semana actual, 30% semana -1, 20% semana -2, 10% semana -3.
4. Ajusta estacionalidad con `brain_search` solo para SKUs top/ambiguos o si hay notes de drop, rebajas, BIS, preorder, weather o retail events. Resume y descarta cada resultado.
5. Declara confianza: alta si hay 4 semanas estables, media si hay restock/drop, baja si hay promo o stockout reciente.

## Stage 5 - Generar propuesta restock

Por SKU:

- SKU/product name.
- Stock total y por almacen.
- ROS 7/14/28.
- WOS actual.
- Units recommended.
- Lead time esperado.
- Proveedor historico si Brain/Stockagile lo permite.
- Razon: stockout prevention, core continuity, BIS demand o cross-market acceleration.

## Stage 6 - DM Slack a the merchandising agent + the merch lead

Envia tabla compacta con:

- SKU
- WOS
- riesgo
- unidades propuestas
- deadline decision
- botones o placeholders `Aprobar` / `Rechazar` si el canal soporta interactividad.

Si no hay interactividad disponible, usa formato: `APPROVE <SKU> <units>` / `REJECT <SKU> <reason>`.

## Anti-patrones

- No proponer restock de SKUs con markdown >40% salvo aprobacion explicita.
- No restock fin-de-temporada sin validar calendario de merchandising.
- Respetar WOS targets por tier si existen en Brain.
- No mezclar stock bloqueado con stock vendible.
- No proponer unidades sin lead time o confianza.

## Tools

- `shopify_query`
- `stockagile_query`
- `brain_search`
- `slack_send_message`

## Cadencia

Daily 8:00 CET.
