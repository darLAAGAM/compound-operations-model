# Onboarding AI — Proceso Obligatorio para Nuevas Incorporaciones

**Actualizado:** 12 abril 2026
**Aplica a:** Toda nueva incorporación (empleados, becarios, freelancers)
**Responsable:** Manager directo + Diego (validación)
**Duración:** 5 minutos (setup) + 1 hora (exploración) = Día 1
**Inspirado en:** Ramp AI Playbook (6300% adoption, 99.5% active users)

---

## Por qué

The reference brand operates a swarm de 8 agentes AI y un "cerebro" compartido con 44 herramientas conectadas a todos los sistemas de la empresa. Cada empleado tiene acceso a este cerebro via Claude Desktop. Esto no es opcional — es parte fundamental de cómo trabajamos.

> *"Mejor pedir perdón que permiso"* — Valor del equipo #2.
> Aplica especialmente a AI: experimenta, construye, comparte.

---

## Cuándo se hace

| Paso | Cuándo | Quién |
|------|--------|-------|
| Welcome Email (existente) | Al confirmar incorporación | Diego |
| Setup AI (este doc) | **Día 1, primera hora** | Nuevo empleado + manager |
| Verificación | **Día 1, antes de comer** | Manager |
| Primer task con AI | **Semana 1** | Nuevo empleado |
| Check L1 | **Día 30** | Manager + Diego |

---

## Paso 1: Setup técnico (5 min)

### 1.1 Instalar Claude Desktop
- Descargar desde https://claude.ai/download
- Crear cuenta o login con email @<brand>.com

### 1.2 Conectar al Cerebro — Un solo comando

Abrir Terminal y pegar:
```
curl -fsSL https://mcp.<brand>.com/setup.sh | bash

irm https://mcp.<brand>.com/setup.ps1 | iex
```

Esto automáticamente instala Node.js, configura la conexión, y verifica todo.
Te pedirá la contraseña del Mac (es normal).

Abrir Claude Desktop — esperar 15-20s — verificar 🔧 con **44+** herramientas.


### Alternativa: Codex (OpenAI GPT-5.4)

Empleados con ChatGPT Plus/Pro pueden conectar Codex al mismo brain:
1. `brew install codex` / `winget install OpenAI.Codex`
2. `codex login`
3. Anadir a `~/.codex/config.toml`:
```toml
[mcp_servers.<brand>]
command = "npx"
args = ["mcp-remote", "https://mcp.<brand>.com/sse"]
```

**Si el comando falla:** Ver guía manual en `knowledge/platform/setup/guia-empleados-cerebro-<brand>.md`

### 1.3 Verificación
El manager verifica que:
- [ ] Claude Desktop abierto y funcionando
- [ ] MCP "<brand>" conectado (icono verde en settings)
- [ ] 44 herramientas visibles
- [ ] `brain_search("the reference brand")` devuelve resultados

**Si algo falla:** Ver `knowledge/platform/setup/claude-desktop-mcp-troubleshooting.md` o pedir ayuda en #ia en Slack.

---

## Paso 2: Prompt de inicialización (1 hora)

Una vez conectado, el nuevo empleado pega el siguiente mensaje como PRIMER mensaje en Claude Desktop.

El prompt completo está en: `knowledge/platform/setup/prompt-inicializacion-empleados.md`

Este prompt hace que Claude:
1. **Lea todo el contexto de the reference brand** — 8 búsquedas temáticas en el brain
2. **Explore el brain completo** — estructura de carpetas, 10-15 docs clave
3. **Audite las herramientas** — verifica que Shopify, Holded, agents, skills funcionan
4. **Memorice 10 reglas permanentes** — Brain First, Brain Write, Datos Reales, Skills Primero, API>Computer, Boris methodology, Subagentes, Council, Branding, Documentar
5. **Escriba lo aprendido** en el brain como prueba de onboarding

### Resultado esperado
Al final del prompt, Claude debe reportar:
- Cuántos docs leyó del brain
- Estado de las herramientas (cuáles funcionan, cuáles no)
- Las 3 cosas más importantes que aprendió sobre the reference brand
- Confirmación de las 10 reglas memorizadas

**El manager revisa este output.** Si las 44 tools funcionan y Claude ha leído el contexto, el setup está completo.

---

## Paso 3: Primer task con AI (Semana 1)

En los primeros 5 días laborables, el nuevo empleado debe completar al menos UNA tarea real usando Claude + el brain. Ejemplos por departamento:

| Departamento | Tarea ejemplo |
|-------------|---------------|
| **Retail** | "Pídele a Claude las ventas de ayer en Barquillo vs Cubí" |
| **Finance** | "Pregunta quién está de vacaciones esta semana" |
| **Marketing/Brand** | "Busca en el brain las brand guidelines y genera 3 opciones de copy para un post" |
| **Producto** | "Consulta el stock actual del producto X en Stockagile" |
| **Wholesale** | "Busca en el brain las reglas de reconciliación wholesale de Gonzalo" |
| **Ecommerce** | "Pide un resumen de GA4 de los últimos 7 días" |
| **CS/Operaciones** | "Consulta los tickets abiertos en Richpanel" |
| **Compras** | "Analiza sell-through de la categoría pantalones en Shopify" |

### Requisitos del primer task:
1. Debe usar al menos 1 herramienta del brain (no vale solo chat genérico)
2. Debe resolver algo real de su trabajo (no un ejercicio inventado)
3. Debe compartir el resultado en **#ia** en Slack con una frase: "Mi primer task con el brain: [descripción]"

---

## Paso 4: Framework de niveles AI (referencia continua)

Inspirado en Ramp. Cada empleado progresa por estos niveles:

### L0 — Observador
- Usa ChatGPT en un tab de vez en cuando
- No ha cambiado ningún workflow
- **Expectativa:** Salir de L0 en la primera semana. Si no hay progreso proactivo, conversación con el manager.

### L1 — Usuario activo
- Claude Desktop conectado al brain y lo usa regularmente
- Hace brain_search antes de preguntar cosas sobre the reference brand
- Ha completado el prompt de inicialización
- **Target:** Todo el equipo en L1 para mayo 2026

### L2 — Constructor
- Ha construido algo que automatiza parte de su trabajo
- Usa skills y herramientas de forma autónoma
- Contribuye escribiendo en el brain (brain_write) cuando aprende algo nuevo
- Comparte en #ia lo que construye
- **Target:** 5-10 personas en L2 para junio 2026

### L3 — Multiplicador
- Construye herramientas/workflows que benefician a otros equipos
- Crea skills nuevos o mejora los existentes
- Enseña a otros cómo usar el brain
- Referente AI en su departamento
- **Target:** 2-3 personas en L3 para septiembre 2026

### Evaluación
- El nivel AI se revisa en los check-ins mensuales
- L0 sostenido (>30 días sin uso del brain) → conversación con manager
- L2+ se celebra en All Hands
- Hiring: nuevas incorporaciones deben demostrar aptitud AI en el proceso de selección

---

## Paso 5: Recursos disponibles

### Documentación
| Recurso | Dónde |
|---------|-------|
| Guía setup completa | `brain: knowledge/platform/setup/guia-empleados-cerebro-<brand>.md` |
| Troubleshooting | `brain: knowledge/platform/setup/claude-desktop-mcp-troubleshooting.md` |
| Prompt de inicialización | `brain: knowledge/platform/setup/prompt-inicializacion-empleados.md` |
| Lista de 44 herramientas | `brain: knowledge/platform/tools/mcp-server-guide.md` |
| 167 skills disponibles | Escribir `skills_list()` en Claude Desktop |

### Canales de ayuda
| Canal | Uso |
|-------|-----|
| **#ia** en Slack | Compartir lo que construyes, pedir ayuda, ver lo que otros hacen |
| **Diego** | Estrategia AI, decisiones sobre nuevas herramientas |
| **Aurelio** (bot en Slack) | Preguntas técnicas sobre el swarm, ayuda con herramientas |

### Agentes AI del equipo
Cada departamento tiene un agente AI especializado que puede ayudar:
- 🦋 **Mafalda** — Customer Service (tickets, respuestas, políticas)
- 📊 **Ferland** — Finanzas (P&L, facturas, cash flow)
- 🏪 **Gala** — Retail (ventas tiendas, stock, tráfico)
- 💻 **Donatello** — Digital (web, ads, email, SEO, analytics)
- 👗 **Olivia** — Merchandising (assortment, pricing, sell-through, wholesale)

Para hablar con ellos: menciónales en Slack (`@Gala ¿ventas de hoy?`) o mándales DM.

---

## Checklist del manager (verificar en Día 1)

- [ ] Claude Desktop instalado y funcionando
- [ ] MCP "<brand>" conectado con 44 herramientas
- [ ] Prompt de inicialización ejecutado y revisado
- [ ] Output del onboarding satisfactorio (docs leídos, tools OK, reglas memorizadas)
- [ ] Empleado sabe cómo acceder a #ia en Slack
- [ ] Empleado tiene asignada su primera tarea AI (Semana 1)
- [ ] Primer task compartido en #ia (verificar en Día 5)

---

## Integración con Welcome Email existente

Añadir este punto después de "Nuestras herramientas" en el welcome email:

```
5) Claude Desktop + Cerebro AI: es nuestro asistente AI conectado a todas las herramientas de the reference brand 
   (Shopify, Holded, Klaviyo, Slack, Google Drive, y más).
   Tu manager te ayudará a configurarlo el Día 1. 
   Mientras tanto, descárgalo: https://claude.ai/download
```

Y añadir al checklist de onboarding existente:
```
7. ⬜ Setup Claude Desktop + Brain MCP (Día 1, con manager)
8. ⬜ Ejecutar prompt de inicialización
9. ⬜ Primer task AI completado y compartido en #ia (Semana 1)
```

---

## Filosofía

> *"The biggest surprise wasn't who built the most. It was how many people had been waiting for permission to build at all."* — Ramp AI Playbook

En the reference brand, esta es la permission. Construye. Experimenta. Comparte. El brain se auto-mejora con cada interacción.

Los 5 valores de the reference brand aplican directamente:
1. **Quien se para pierde** → Usar AI no es opcional, es evolucionar
2. **Mejor pedir perdón que permiso** → Experimenta con el brain sin esperar aprobación
3. **Lo perfecto es enemigo de lo bueno** → Un prompt imperfecto que se ejecuta > un plan perfecto que no se ejecuta
4. **Paso corto, mirada larga** → Empieza con una tarea pequeña hoy, construye el músculo AI con el tiempo
5. **Cada euro cuenta** → AI multiplica la productividad sin coste adicional (ya tenemos la infraestructura)
