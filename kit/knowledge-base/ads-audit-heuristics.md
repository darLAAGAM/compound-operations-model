# Heurísticas de Auditoría de Ads — Checklist Donatello

*Cherry-picked de [claude-ads](https://github.com/AgriciDaniel/claude-ads) — 10 abril 2026*
*Adaptado para LAAGAM (E-commerce DTC Fashion, Meta + Google + Pinterest)*
*46 checks Meta + 74 checks Google originales → filtrado a lo aplicable*

---

## Reglas de decisión rápida (las más importantes)

### 🔴 3× Kill Rule (PARAR INMEDIATAMENTE)
**Si el spend > 3× target CPA y 0 conversiones → PAUSAR campaña.**
Revisar: creativo, targeting, landing page, tracking. No reactivar sin cambios.

### 🟢 20% Scale Rule (ESCALAR)
**Si CPA actual < target CPA en >10% + campaña fuera de learning phase → subir budget 20%.**
Esperar 3-5 días entre incrementos. NUNCA superar 20% de incremento de golpe en Meta.

### 🟡 Decreasing Returns (ROLLBACK)
**Si CPA sube >15% tras incremento de budget → revertir.**
Esperar 7 días antes de intentar scaling horizontal (nuevas audiences o plataformas).

### 📊 Señales de saturación
| Plataforma | Señal | Umbral | Acción |
|------------|-------|--------|--------|
| Google | Impression Share | >80% | Diversificar — rendimientos decrecientes |
| Meta | Frequency 7d | >4.0 | Refrescar creativo, expandir audience |
| TikTok | Frequency | >3.0 | Reemplazar assets creativos |

---

## Budget allocation para LAAGAM (E-commerce DTC)

### Split recomendado
| Plataforma | % Budget | Rol |
|------------|----------|-----|
| Meta | 50-68% | Core performance + ASC |
| Google PMax/Search | 23-30% | Intent capture |
| TikTok | 5-15% | Awareness + UGC |
| Email (Klaviyo) | 5% | Retention |

### Distribución 70/20/10
- **70%** → campañas con performance positivo establecido
- **20%** → campañas con tracción que necesitan escalar
- **10%** → experimental (nuevas plataformas, audiences, formatos)

---

## Meta Ads — Checks prioritarios para LAAGAM

### 🔴 CRÍTICOS (resolver inmediatamente)
| Check | Qué | Pass | Warning | Fail |
|-------|-----|------|---------|------|
| M02 | CAPI (Conversions API) activo | Server-side + pixel | Planificado | Ausente (30-40% data loss) |
| M03 | Event deduplication via event_id | ≥90% dedup | <90% | Sin event_id |
| M04 | Event Match Quality Purchase | ≥8.0 | 6.0-7.9 | <6.0 |
| M13 | Learning phase status | <30% "Learning Limited" | 30-50% | >50% |
| M25 | Format diversity | ≥3 formatos | 2 | 1 solo |
| M28 | Creative fatigue | Sin CTR drop >20% en 14d | 10-20% drop | >20% + freq >3 |

### 🟡 ALTOS (resolver en 7 días)
| Check | Qué | Pass | Warning | Fail |
|-------|-----|------|---------|------|
| M11 | Campañas por país/funnel | ≤5 | 6-8 | >8 (fragmentación) |
| M12 | CBO vs ABO | CBO >$500/d, ABO <$100/d test | - | CBO en <$100/d |
| M16 | Audience overlap | Sin overlap | <20% | >30% |
| M19 | Audience overlap general | <20% | 20-40% | >40% |
| M23 | Exclusiones de compradores | Purchasers excluidos de prospecting | Parcial | Ninguna |
| M26 | Creativos por ad set | ≥5 (ideal 5-8) | 3-4 | <3 |
| M31 | Contenido UGC/social-native | ≥30% assets | 10-30% | <10% |
| M-CR1 | Freshness creativa | Nuevo asset en <30 días | 30-60d | >60d sin refresh |
| M-CR2 | Frequency prospecting | <3.0 (7d) | 3.0-5.0 | >5.0 |
| M-ST1 | Budget vs CPA | Diario ≥5× target CPA | 2-5× | <2× |

### 🟢 MEDIOS (resolver en 30 días)
| Check | Qué | Pass | Fail |
|-------|-----|------|------|
| M15 | Advantage+ Sales (ASC) | Activa para e-commerce | Sin testar |
| M22 | Advantage+ Audience | Testada vs manual | Sin testar |
| M30 | Social proof | Top posts orgánicos boosted | Ninguno |
| M32 | Advantage+ Creative | Enhancements con testing | Sin testar |
| M39 | UTM parameters | En todas las URLs | Ninguna |

---

## Google Ads — Checks prioritarios para LAAGAM

### 🔴 CRÍTICOS
| Check | Qué | Pass | Warning | Fail |
|-------|-----|------|---------|------|
| G42 | ≥1 conversión primaria configurada | Sí | - | No |
| G43 | Enhanced conversions activas | Sí | - | No |
| G05 | Brand vs non-brand separados | Campañas separadas | - | Mezclados |
| G37 | Target CPA/ROAS vs histórico | Dentro de ±20% | 20-50% off | >50% off |
| G21 | Keywords con QS ≤3 | <10% | 10-25% | >25% |

### 🟡 ALTOS
| Check | Qué | Pass | Warning | Fail |
|-------|-----|------|---------|------|
| G13 | Search terms revisados | <14 días | <30 días | >30 días |
| G14 | Negative keyword lists | ≥3 listas temáticas | - | <3 |
| G16 | Wasted spend | <5% en irrelevantes | 5-15% | >15% |
| G20 | QS medio ponderado | ≥7 | 5-6 | ≤4 |
| G26 | RSA por ad group | ≥1 (2+ recomendado) | - | Ninguno |
| G31 | PMax assets: ≥20 images, ≥5 logos, ≥5 videos | Completo | - | Incompleto |
| G36 | Smart Bidding si ≥15 conv/30d | Automated | - | Manual CPC con data |
| G59 | Landing page LCP móvil | <2.5s | 2.5-4.0s | >4.0s |

---

## Quick Wins (alto impacto, <15 min)

### Meta
| Acción | Tiempo |
|--------|--------|
| Deploy CAPI Gateway | 15 min |
| Verificar dominio en Business Manager | 5 min |
| Set atribución 7-day click / 1-day view | 2 min |
| Crear Custom Audience purchasers, excluir prospecting | 10 min |
| Añadir video/carousel a ad sets solo imágenes | 15 min |
| Añadir UTM template a nivel campaña | 5 min |

### Google
| Acción | Tiempo |
|--------|--------|
| Enable Enhanced Conversions | 5 min |
| "People in" location targeting (no "interested in") | 2 min |
| Crear listas temáticas de negativos | 10 min |
| Desactivar Display Network en campañas Search | 2 min |
| Separar brand en campaña propia | 10 min |
| Añadir 4+ sitelinks | 10 min |

---

## Scoring System (para audit reports de Donatello)

### Fórmula
```
Score = Σ(Check_pass × Weight_severity × Weight_category) / Σ(Check_total × Weight_severity × Weight_category) × 100
```

### Multiplicadores de severidad
| Severidad | Multiplicador |
|-----------|--------------|
| Critical | 5.0 |
| High | 3.0 |
| Medium | 1.5 |
| Low | 0.5 |

### Resultados por check
- **PASS** → puntos completos
- **WARNING** → 50% puntos
- **FAIL** → 0 puntos
- **N/A** → excluido del cálculo

### Escala de notas
| Nota | Rango | Status |
|------|-------|--------|
| A | 90-100 | Excelente |
| B | 75-89 | Bueno |
| C | 60-74 | Necesita mejora |
| D | 40-59 | Pobre |
| F | <40 | Crítico |

### Pesos por categoría (Meta)
| Categoría | Peso |
|-----------|------|
| Pixel/CAPI Health | 30% |
| Creative (diversidad + fatiga) | 30% |
| Account Structure | 20% |
| Audience & Targeting | 20% |

### Pesos por categoría (Google)
| Categoría | Peso |
|-----------|------|
| Conversion Tracking | 25% |
| Wasted Spend/Negatives | 20% |
| Account Structure | 15% |
| Keywords & Quality Score | 15% |
| Ads & Assets | 15% |
| Settings & Targeting | 10% |

### Multi-plataforma
```
Score agregado = Σ(Score_plataforma × Budget_share_plataforma)
```

---

## Deprecation notices relevantes (2025-2026)

- **ECPC (Enhanced CPC):** Deprecado marzo 2025 para nuevas campañas. Migrar a tCPA/tROAS/Max Conversions.
- **Call Campaigns Google:** Sin nuevas desde febrero 2026. Migrar a Search + call assets antes de febrero 2027.
- **Meta Detailed Targeting Exclusions:** Eliminadas enero 2026. Usar Custom Audience exclusions o Advantage+ Audience.
- **Google DDA:** Data-driven attribution ahora default. Rule-based models deprecados septiembre 2025.

---

## Cómo usar esto en el swarm

1. **Donatello** debe correr este checklist mensualmente contra las campañas activas de Meta y Google.
2. Usar `meta_ads_query` y `ga4_query` del MCP para obtener datos reales.
3. Generar un "Ads Health Score" con la fórmula de scoring.
4. Quick Wins con severidad Critical/High y <15 min → ejecutar inmediatamente (con aprobación Diego/equipo marketing).
5. Reportar en `#marketing` o en el weekly report.

**Trigger:** Diego puede pedir "/audit meta" o "/audit google" y Donatello ejecuta el checklist relevante.
