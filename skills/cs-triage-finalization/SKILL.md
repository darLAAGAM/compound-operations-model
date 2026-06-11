---
name: cs-triage-finalization
description: "CS triage closure para the CS agent: escalations, UPS duties mal cobrados (Global-e DDP), DHL label regeneration y baseline metrics. Cierra el 40% de drafts aun no automatizados."
metadata:
  source: the company-native
  category: customer_support
  primary_user: cs-agent
  owner: laura
  cadence: continuous + weekly_review
  tools_needed: richpanel_query, shopify_query, slack_send_message, brain_search
---

> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._


# CS Triage Finalization

## What it does

Cierra la capa de triage CS que todavia queda manual: patrones recurrentes de escalacion, deteccion de UPS duties mal cobrados cuando Global-e ya marco DDP, regeneracion de DHL labels afectadas por Rever, y metricas baseline para saber si los drafts pendientes bajan de forma sostenida.

El output no es una respuesta al cliente. El output es una cola de drafts internos, agrupaciones de patrones y alertas para Laura/the CS agent con evidencia suficiente para aprobar, ajustar template o escalar.

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

- the CS agent lo activa antes de cada barrido de inbox.
- Laura lo invoca cuando detecta un patron recurrente sin template o con respuestas inconsistentes.
- Usalo cuando el inbox tenga volumen alto de drafts abiertos, escalations repetidas o dudas sobre duties/labels.

## Stage 1 - Pattern detection en ultimos 30 dias

1. Ejecuta `richpanel_query` sobre tickets/drafts de los ultimos 30 dias con `limit=20` y campos minimos: `id,subject,status,tags,owner,created_at,updated_at,last_message_at,order_id,draft_status`. No traigas body completo ni attachments en esta fase.
2. Resume y descarta el raw: cuenta estados abiertos/pending/escalated/refunded-requested/drafts sin envio, mediana aproximada de antiguedad y owners principales.
3. Agrupa tematicamente usando solo `subject`, `tags` y metadatos: shipping delay, duties, return label, size exchange, damaged item, refund status, order edit, address issue, payment issue, retail/POS.
4. Para cada cluster devuelve volumen, % sobre muestra, owner principal y 1-2 ejemplos por `id + subject`; no pegues conversaciones completas.
5. Ejecuta `brain_search` solo para los 2-3 clusters mas relevantes, resume policies/templates encontrados en <=300 tokens y descarta raw antes de redactar.

## Stage 2 - Auto-classification rules

Clasifica cada conversation en una de estas salidas:

- `escalation`: requiere decision humana, excepcion de policy, riesgo legal/PR, VIP, amenaza chargeback, valor alto o datos operativos contradictorios.
- `auto-draft`: hay policy clara, datos de pedido completos y no se ejecuta accion irreversible.
- `noise-close`: duplicado, out-of-office, spam, cliente ya respondido por otro canal o ticket sin accion tras cierre verificado.

Regla de seguridad: ante duda entre auto-draft y escalation, elige escalation con evidencia corta.

## Stage 3 - UPS duty detection

Objetivo: detectar duties UPS cobrados al cliente aunque el checkout Global-e fuera DDP.

1. Primero consulta `richpanel_query` con ventana 7d, `limit=20` y `fields=id,subject,tags,order_id,created_at,attachments_count` filtrando UPS/duties/Global-e/DDP. Resume ids y order_ids; descarta raw.
2. Solo para los `order_id` candidatos, consulta `shopify_query` con `limit=50` y `fields=id,name,market,shipping_address.country,tags,total_duties_set,total_tax_set,financial_status,fulfillment_status,shipping_lines`.
3. Resume y descarta Shopify raw antes de cruzar: flag si order marcado DDP + cliente adjunta duty invoice/cobro UPS + destino cubierto por Global-e.
4. Genera draft refund interno con importe, evidencia por ids y plantilla. No ejecutes refund.
5. Envia alerta a Laura por `slack_send_message` si hay varios casos del mismo mercado o carrier en 24h.

## Stage 4 - DHL label health check

Detecta el bug Rever/DHL donde la label no se genera, se regenera con error o queda bloqueada.

1. Busca tickets 14d con DHL, label, return, exchange, Rever, QR, etiqueta o error usando `richpanel_query limit=20 fields=id,subject,tags,order_id,status,created_at,last_message_at`. No traigas bodies salvo para 1-2 casos ambiguos.
2. Resume candidatos y descarta raw.
3. Cruza solo `order_id` candidatos con `shopify_query limit=50 fields=id,name,fulfillment_status,return_status,tags,created_at,shipping_lines`.
4. Clasifica: regenerate label, manual carrier fallback, escalation to ops, customer education.
5. El draft debe incluir accion interna, no un envio publico automatico.

## Anti-patrones

- No enviar drafts al cliente desde este skill.
- Siempre crear notas/drafts como `is_operator=true` y `public=false` cuando la herramienta lo permita.
- Nunca ejecutar refund automatico sin aprobacion de Laura.
- No cerrar ruido si falta una verificacion de pedido o si el cliente espera respuesta.
- No inventar policy: buscar en Brain y sistemas fuente.

## Tools

- `richpanel_query` para inbox, conversations, tags, drafts y attachments.
- `shopify_query` para order truth, payments, duties, fulfillments y refunds.
- `slack_send_message` para alerts a Laura/the CS agent.
- `brain_search` para policies, templates y gotchas.

## Cadencia

- Continuo: the CS agent antes de cada barrido inbox.
- Weekly review: Laura revisa clusters, baseline, templates nuevos y excepciones.
