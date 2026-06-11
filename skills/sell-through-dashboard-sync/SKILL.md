---
name: sell-through-dashboard-sync
description: "Sync automatico del sell-through dashboard SS26. Pull Shopify ventas + Stockagile stock + ROS/WOS/ST/Dispuesto por SKU, actualiza Sheet y alerta Slack."
metadata:
  source: the company-native
  category: merchandising
  primary_user: merchandising-agent
  owner: melissa_ibarra
  cadence: four_times_daily
  tools_needed: shopify_query, stockagile_query, google_workspace, slack_send_message, brain_search
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# Sell-Through Dashboard Sync

## What it does

Sincroniza automaticamente el sell-through dashboard SS26 en Google Sheets (`1z4ojnwX...`). Cruza Shopify ventas, Stockagile stock multi-warehouse y calcula ROS, WOS, ST% y Dispuesto por SKU. Actualiza el dashboard 4 veces al dia y alerta a Melissa Ibarra solo cuando hay cambios accionables.

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

- Cron cada 6h.
- Manual si Melissa, the merchandising agent o Diego piden estado SS26, riesgo de rotura o exceso por SKU.
- Antes de reuniones de merchandising donde se decidan palancas comerciales.
- Parametro obligatorio: `category` o lista corta de categorias/SKUs. No ejecutar sobre full catalog. En rehearsal validado con `DR-L` y `BL-L`.

## Stage 1 - Pull Shopify orders

1. Requiere `category`/categoria acotada antes de consultar. Si no viene, pide una categoria o usa solo las 2 categorias explicitadas por el caller; no hagas full catalog.
2. Usa `shopify_query` para agregacion por SKU y semana de los ultimos 28 dias por defecto, con fallback 90d solo si el SKU no tiene historia suficiente: `group_by=sku,week`, `limit=50`, `fields=sku,product_title,variant_title,week,quantity,net_revenue,discounts,refunds,channel,country,created_at`.
3. Filtra por categoria/SKU server-side y excluye cancelaciones, test orders y ventas internas si estan etiquetadas.
4. Resume en <=300 tokens: unidades/revenue por SKU, semanas disponibles y excepciones. Descarta raw antes de Stage 2.

## Stage 2 - Pull Stockagile stock

Usa `stockagile_query` solo para los SKUs de la categoria acotada o los SKUs resultantes del Stage 1, maximo 50, con `fields=sku,product_name,category,warehouse,available,reserved,blocked,in_transit,buy_units` para stock actual por SKU y warehouse:

- Stockabee
- Store B
- Store A
- Amphora
- Amsterdam

Separar disponible, reservado, bloqueado y en transito cuando la fuente lo permita. Resume y descarta raw antes de calcular metricas.

## Stage 3 - Calcular metricas por SKU

- `ROS`: unidades vendidas por semana, preferentemente trailing 4 semanas con fallback 90d.
- `WOS`: stock disponible / ROS semanal.
- `ST%`: vendido / dispuesto.
- `Dispuesto`: vendido + stock disponible + reservado/en transito si aplica al buy original.

Si falta el buy original, marca `Dispuesto` como no verificado y no inventes ST%.

## Stage 4 - Categorizar por umbral

- `RED`: WOS < 4, urgente.
- `YELLOW`: WOS 4-12, optimo.
- `ORANGE`: WOS 12-30, activar palancas.
- `BLACK`: WOS > 100, peso muerto.

Incluye columna `reason` con una frase: "high ROS low stock", "healthy", "slow mover", "dead weight", "missing buy", "recent drop insufficient history".

## Stage 5 - Push a Google Sheet

Usa `google_workspace` con cuenta the company autorizada para actualizar el Sheet:

- Mantener headers estables.
- Escribir timestamp de sync.
- No romper formulas existentes; escribe solo rangos destinados a datos raw/sync.
- Escribir solo la pestaña/rango de la categoria procesada; no borrar ni reconstruir todo el workbook.
- Si la API falla, reporta error exacto y deja payload listo para retry.

## Stage 6 - Alertas Slack

Envia `slack_send_message` a Melissa solo cuando:

- Un SKU core entra nuevo en `RED`.
- Aparece una nueva `ORANGE`.
- Un SKU cambia a `BLACK`.
- Hay fallo de sync que deja datos stale >6h.

Evita alert fatigue: no repetir la misma alerta si no cambio estado desde el ultimo sync.

## KPI tracking

- Forecast accuracy.
- Stockouts <5%.
- DIO <160d.

## Tools

- `shopify_query`
- `stockagile_query`
- `google_workspace`
- `slack_send_message`
- `brain_search`

## Cadencia

4x/dia: 00:00, 06:00, 12:00, 18:00 CET.
