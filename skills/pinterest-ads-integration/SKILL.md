> _Public, anonymized version of a skill running in the Compai reference deployment (an 8-figure consumer SME). Names, stores, channels and endpoints replaced with placeholders; the logic is unchanged. Adapt to your own context._

# Pinterest Ads — Skill de uso para agentes

*Para: TODOS los agentes del swarm (acceso via MCP)*
*Owner: the marketing agent (primary) — Diego, the strategy hub, the CS agent, the retail agent, the merchandising agent, the finance agent, the people agent tienen acceso*

## Tool

`pinterest_ads_query(endpoint, method="GET", params="")`

Disponible para **todos** los agentes via MCP. Token OAuth con auto-refresh (no expira).

## Cuándo usarla

| Caso | Quién | Tool call |
|------|-------|-----------|
| ¿Cuánto gastamos en Pinterest este mes? | the marketing agent, the finance agent | `analytics?columns=SPEND_IN_DOLLAR&granularity=TOTAL` |
| ¿Qué campañas tenemos activas? | the marketing agent | `ad_accounts/{id}/campaigns` |
| ¿CTR / clicks por campaña? | the marketing agent | `analytics?columns=CAMPAIGN_NAME,CTR,CLICKTHROUGH_1&granularity=TOTAL` |
| ¿Followers/views del perfil? | the CS agent, the marketing agent | `user_account` |
| ¿Cuántos pins tenemos? | the marketing agent, the merchandising agent | `user_account` (campo pin_count) |

## Ejemplos copy-paste

### 1. Top-line metrics del mes
```
pinterest_ads_query("ad_accounts/549759188046/analytics",
    params="start_date=2026-04-01&end_date=2026-04-30&columns=SPEND_IN_DOLLAR,IMPRESSION_1,CLICKTHROUGH_1,CTR&granularity=TOTAL")
```

### 2. Performance diaria
```
pinterest_ads_query("ad_accounts/549759188046/analytics",
    params="start_date=2026-04-01&end_date=2026-04-15&columns=SPEND_IN_DOLLAR,CLICKTHROUGH_1,CTR&granularity=DAY")
```

### 3. Por campaña
```
pinterest_ads_query("ad_accounts/549759188046/campaigns", params="page_size=25")
```

Luego:
```
pinterest_ads_query("ad_accounts/549759188046/analytics",
    params="start_date=2026-04-01&end_date=2026-04-15&columns=CAMPAIGN_NAME,SPEND_IN_DOLLAR,CTR,CLICKTHROUGH_1&granularity=TOTAL&campaign_ids={ids}")
```

### 4. Perfil Pinterest
```
pinterest_ads_query("user_account")
# Returns: follower_count, monthly_views, pin_count, board_count, account_type, business_name
```

### 5. Listado ad accounts
```
pinterest_ads_query("ad_accounts")
# Returns: id, name, currency, country, time_zone, permissions
```

## Configuración técnica

- **Ad Account ID:** `549759188046` (the company, EUR, Europe/Madrid)
- **Pinterest username:** @your-brand
- **Scopes activos:** `ads:read boards:read catalogs:read pins:read user_accounts:read`
- **API base:** `https://api.pinterest.com/v5/`
- **Auth:** OAuth refresh tokens, auto-refresh diario via systemd timer
- **Token storage:** `/etc/the company/pinterest_tokens.json` (root only, no manipular manualmente)
- **Token manager:** `<your-services-dir>/pinterest_token_manager.py`

## Columnas analytics válidas (más usadas)

- `SPEND_IN_DOLLAR` — gasto total USD
- `SPEND_IN_MICRO_DOLLAR` — gasto en micro-USD (÷1,000,000)
- `IMPRESSION_1` — impresiones
- `CLICKTHROUGH_1` — clicks
- `CTR` — click-through rate (decimal, multiplicar ×100 para %)
- `CPC_IN_DOLLAR` — coste por click
- `ECPM_IN_MICRO_DOLLAR` — eCPM
- `OUTBOUND_CLICK_1` — clicks fuera de Pinterest
- `ENGAGEMENT_1` — engagements totales
- `REPIN_1` — repins
- `CAMPAIGN_NAME`, `AD_GROUP_NAME`, `PIN_ID` — para breakdown

**⚠️ NO usar:** `SPEND_IN_EURO` (no existe) — Pinterest siempre en USD

## Granularity

- `TOTAL` — un solo agregado
- `DAY` — desglose diario
- `HOUR` — desglose horario
- `WEEK` — desglose semanal
- `MONTH` — desglose mensual

## Limitaciones actuales

- **Solo lectura** (scopes `:read`). Para escribir/pausar campañas hay que pedir Standard tier
- **Sin acceso a Catalogs** todavía a través de v5 (solo lectura básica)
- **Datos en USD**, convertir manualmente si necesitas EUR

## Si algo falla

1. Check estado del token: `python3 <your-services-dir>/pinterest_token_manager.py status`
2. Force refresh: `python3 <your-services-dir>/pinterest_token_manager.py refresh`
3. Si "401 unauthorized" → revisar log `/var/log/pinterest-token-refresh.log`
4. Si refresh_token expirado (60d sin uso) → contactar a Diego para repetir OAuth flow
5. Doc completo: `knowledge/platform/tools/pinterest-api-setup.md`
