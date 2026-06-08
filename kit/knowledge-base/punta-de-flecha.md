# Punta de Flecha — Convergencia Adversarial Cross-Model

*Creado: 11 abril 2026*
*Autor: Diego Arroyo*
*Tipo: Skill de deliberación estratégica*

---

## Concepto

Método de análisis estratégico que enfrenta **dos modelos de IA de diferente arquitectura** en iteraciones sucesivas hasta alcanzar convergencia. Cada modelo revisa, critica y refina el output del otro, afilando progresivamente el análisis como una punta de flecha.

**Diferencia vs. council_query:**
- Council = 6 perspectivas, 1 modelo (Claude), 1 ronda → mismos biases
- Punta de Flecha = 2+ modelos (Claude + GPT), N rondas iterativas → cross-architecture, convergencia verificable

## Arquitectura de referencia

```
┌─────────────────────┐     ┌──────────────────────┐
│ MODELO A             │     │ MODELO B              │
│ Claude Opus 4.6      │     │ GPT-5.4               │
│ (Claude Code / yo)   │◄───►│ (Aurelio via agent_send)│
│                      │     │ OAuth ChatGPT Diego   │
│ Coste: €0 (Max)      │     │ Coste: €0 (Plus/Pro)  │
└─────────────────────┘     └──────────────────────┘
         │                           │
         └─────── ITERACIÓN ─────────┘
              hasta convergencia
```

## Protocolo paso a paso

### Fase 0: Preparación
- Definir la **pregunta estratégica** con claridad
- Si hay documentos de contexto: consolidarlos en un único bloque de texto
- Definir **criterio de éxito** (qué tipo de output esperas: recomendación, plan, análisis)

### Fase 1: Análisis inicial paralelo (Round 0)
- **Modelo A (Claude):** genera análisis completo de la pregunta
- **Modelo B (GPT-5.4 via Aurelio):** genera su análisis independiente, SIN ver el de Claude
- Esto garantiza análisis no contaminados con diferentes biases de architecture

### Fase 2: Punta de Flecha (Rounds 1-N)
```
LOOP:
  1. Output de Modelo A → se envía a Modelo B con prompt:
     "Un comité de expertos independiente ha generado este análisis.
      Revísalo críticamente:
      - ¿Estás de acuerdo? ¿Por qué sí/no?
      - ¿Qué falta o es incorrecto?
      - ¿Qué añadirías, matizarías o eliminarías?
      Genera un análisis mejorado incorporando tus correcciones."

  2. Output refinado de Modelo B → se envía a Modelo A con el mismo prompt

  3. Check convergencia:
     - Si delta entre Round N y N-1 es cosmético → STOP
     - Si ambos modelos dicen "no puedo mejorar esto" → STOP
     - Si Round > 10 → STOP (rendimientos decrecientes)
     
  4. Si no convergencia → CONTINUE LOOP
```

### Fase 3: Síntesis final
- El modelo que termina la última iteración genera:
  1. **Recomendación final** (clara, accionable, con posición firme)
  2. **Puntos de consenso** (en qué ambos modelos convergieron)
  3. **Divergencias resueltas** (qué cambió durante las iteraciones y por qué)
  4. **Divergencias irresolubles** (si las hay — igual de valiosas)
  5. **Nivel de confianza** (HIGH/MEDIUM/LOW con justificación)
  6. **Next steps** concretos (max 5)

## Cuándo usar Punta de Flecha vs. Council

| Situación | Usar |
|-----------|------|
| Pregunta rápida táctica (<5 min) | Ni uno ni otro — respuesta directa |
| Pregunta estratégica estándar (~10 min) | `council_query` (1 ronda, rápido, bueno) |
| Decisión de alto impacto (>€50K, irreversible, alta incertidumbre) | **Punta de Flecha** |
| Análisis que requiere máxima precisión | **Punta de Flecha** |
| Investigación con datos complejos/contradictorios | **Punta de Flecha** |

## Invocación

### Opción 1: Via Claude Code (Diego)
Diego pide directamente: "Punta de Flecha: ¿deberíamos [pregunta]?"
Claude Code actúa como Modelo A, usa `agent_send("aurelio", ...)` para Modelo B.

### Opción 2: Via MCP tool
```
punta_de_flecha("¿Deberíamos abrir tienda en Salamanca?", max_rounds=5)
```
El tool en server.py orquesta automáticamente Claude (API) vs GPT-5.4 (Aurelio).

### Opción 3: Manual
Diego cruza outputs entre Claude (chat) y ChatGPT (chat) manualmente.
Más lento pero funciona sin infra.

## Prompt para el cruce (template)

```
Eres parte de un proceso de deliberación adversarial cross-model.
Otro comité de expertos, usando una arquitectura de IA diferente a la tuya,
ha generado el siguiente análisis sobre la pregunta:

PREGUNTA: {pregunta}

ANÁLISIS DEL OTRO COMITÉ (Round {N}):
{output_otro_modelo}

Tu tarea:
1. Revisa críticamente este análisis punto por punto
2. Señala lo que es correcto, incorrecto, incompleto o sesgado
3. Aporta datos, perspectivas o frameworks que falten
4. Si estás sustancialmente de acuerdo, di POR QUÉ y refuerza los puntos clave
5. Genera un ANÁLISIS MEJORADO que incorpore lo mejor de ambos

Si crees que el análisis es excelente y no puedes mejorarlo materialmente,
di: "CONVERGENCIA ALCANZADA" y explica por qué.

Sé específico, cuantitativo donde puedas, y decisivo. No seas tibio.
```

## Aplicación a OperAI

Este método es **replicable para cualquier cliente OperAI**:
- Cualquier swarm con 2+ modelos puede ejecutar Punta de Flecha
- El requisito mínimo es acceso a 2 LLMs de diferente architecture
- Se documenta como patrón en el playbook OperAI
- Diferenciador competitivo: ningún competidor ofrece deliberación cross-model iterativa

## Extensiones futuras

1. **3+ modelos:** Añadir Perplexity Sonar Pro (tiene web search nativo) como tercer modelo para triangular
2. **Punta de Flecha con datos:** Antes de cada round, el modelo busca datos frescos (web, brain, APIs) para fundamentar
3. **Punta de Flecha sectorial:** Adaptar el prompt de cruce al sector (retail, finance, healthcare, etc.)
4. **Auto-scheduling:** Para decisiones big-ticket, programar una Punta de Flecha automática con resultados en #strategy

## Origen

Metodología desarrollada por Diego Arroyo (abril 2026) en el contexto de análisis médico
(caso real de cáncer metastásico con resultados verificados), adaptada a business strategy.
El principio subyacente (adversarial convergence across architectures) es domain-agnostic.
