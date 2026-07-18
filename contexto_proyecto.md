# ⚖️ DesnaturalizaCheck

> **Asistente Inteligente de Diagnóstico de Laboralidad y Cálculo de Liquidaciones por Desnaturalización de Contratos**
> *Hackathon 12h · Python + Streamlit + DuckDB/Parquet + SBERT · RTX 5060 (8 GB VRAM)*

---

## 1 · Análisis de la propuesta original

### ✅ Fortalezas (se conservan)

| Fortaleza                    | Por qué importa                                                                                                                                                                        |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nicho cerrado y validado** | <mark>2,589 registros reales de desnaturalización</mark> filtrados de `poder_judicial_data_completa.json` (134,796). Corpus pequeño → búsqueda instantánea, cero problemas de memoria. |
| **Motor determinístico**     | La liquidación se calcula con **fórmulas legales, no con ML** → no puede alucinar ni fallar en vivo. El riesgo técnico más bajo posible.                                               |
| **Wow factor monetario**     | *"El empleador te debe S/ 24,350"* es el output más contundente que puede mostrar una demo: convierte la ley en dinero.                                                                |
| **Impacto social directo**   | Locadores y CAS son el grupo más grande de informalidad encubierta del país; el acceso a un abogado es la barrera real.                                                                |
| **Completitud de datos**     | `metadata_pretension` 96.71% y `abstract` 81.21% → sumillas limpias suficientes para retrieval sin procesar cuerpos completos.                                                         |

### ⚠️ Debilidades detectadas (y su corrección)

| # | Debilidad | Riesgo | Corrección aplicada |
|---|---|---|---|
| D1 | Afirmar **"100% de precisión"** | Un jurado técnico o abogado lo destruye en la primera pregunta. Ningún diagnóstico legal es 100% certero. | Reformular como: <mark>"cálculo determinístico auditable + diagnóstico orientativo con score explicable"</mark>. La precisión del 100% aplica solo a la **aritmética de la liquidación**, no al pronóstico judicial. |
| D2 | **Mezcla de regímenes incompatibles**: DL 728 (privado), Ley 24041 (público 276) y CAS (DL 1057) tienen consecuencias jurídicas distintas | La desnaturalización CAS/276 suele dar **reposición**, no beneficios del 728; mezclar fórmulas produce liquidaciones jurídicamente inválidas. | Añadir un **selector de régimen** como primer paso del wizard. Cada régimen activa su propio motor de reglas y su propio subconjunto de jurisprudencia. |
| D3 | Ignora el **precedente Huatuco** (Cas. 5057-2013-Junín) | En el sector público, la reposición exige plaza presupuestada y concurso público de ingreso. Prometer reposición sin ese matiz es incorrecto. | El reporte del régimen público incluye un **bloque de advertencia Huatuco** con las excepciones (obreros municipales, carrera especial, etc.). Esto además <mark>demuestra sofisticación jurídica ante el jurado</mark>. |
| D4 | No considera la **prescripción laboral** (Ley 27321: 4 años desde el cese) | Calcular beneficios de hace 10 años infla la liquidación y desinforma. | El motor financiero **corta automáticamente los periodos prescritos** y lo muestra en el desglose ("S/ X reclamables · S/ Y prescritos"). Detalle pequeño, credibilidad enorme. |
| D5 | El "semáforo de probabilidad" no explica su origen | Un score black-box en materia legal es indefendible. | Sustituir por un <mark>**scorecard explicable de indicios de laboralidad**</mark> (ver §4): cada respuesta suma puntos visibles, con sustento en el principio de **primacía de la realidad**. |

> **Decisión del análisis: ✅ APROBADO CON MEJORAS.** La idea es la más equilibrada del portafolio (riesgo técnico mínimo + wow máximo). Las correcciones D1–D5 no agregan tiempo de desarrollo significativo y blindan la demo ante cualquier jurado con formación legal.

---

## 2 · Propuesta de valor mejorada

**El problema.** Miles de trabajadores peruanos emiten recibos por honorarios o encadenan contratos CAS temporales cuando en la práctica cumplen horario, reciben órdenes y usan recursos del empleador. No perciben CTS, gratificaciones ni vacaciones, y <mark>evaluar su caso con un abogado cuesta más de lo que muchos ganan en un mes</mark>.

**La solución.** Una plataforma de autoservicio gratuita en 3 pasos:

1. **Diagnóstico** — wizard de indicios de laboralidad (2 minutos).
2. **Liquidación** — cálculo automático de beneficios truncos con fórmulas oficiales.
3. **Evidencia** — las 3 sentencias reales del Poder Judicial más parecidas a su caso.

**El resultado visual.** Un **semáforo explicable** de solidez del caso + un **reporte PDF descargable** con la liquidación detallada línea por línea y los precedentes citados — listo para llevar a una consulta legal o a SUNAFIL.

> 💡 **Pitch de 10 segundos:** *"Respondes 10 preguntas y te decimos cuánto te debe tu empleador — con las sentencias que lo prueban."*

---

## 3 · Arquitectura técnica final (Implementada)

```
┌─────────────────────┐     ┌──────────────────────────┐     ┌─────────────────────┐
│  WIZARD STREAMLIT   │────▶│  MOTOR DE DIAGNÓSTICO    │────▶│  MOTOR FINANCIERO   │
│  (régimen + hechos  │     │  Scorecard de indicios   │     │  Reglas DL 728 /    │
│   + sueldo + fechas)│     │  (primacía realidad)     │     │  L.24041 / DL 1057  │
└──────────┬──────────┘     └──────────────────────────┘     └──────────┬──────────┘
           │                                                            │
           ▼                                                            ▼
┌─────────────────────┐     ┌──────────────────────────┐     ┌─────────────────────┐
│  GRÁFICOS & STATS   │     │  RETRIEVAL SENTENCIAS    │◀───▶│  DuckDB + Parquet   │
│  (st.bar_chart +    │     │  SBERT + coseno sobre    │     │  (Fusión scraper    │
│   Tasa de Éxito DB) │     │  13,871 abstracts        │     │   incremental)      │
└──────────┬──────────┘     └─────────────┬────────────┘     └─────────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐     ┌──────────────────────────┐
│  REPORTE PDF        │◀────│  ENLACES EXPEDIENTES     │
│  (fpdf2 - completo  │     │  (Descarga directa del   │
│   con intereses)    │     │   PDF oficial del PJ/TC) │
└─────────────────────┘     └──────────────────────────┘
```

| Capa            | Implementación                                                                                                                                                               | Justificación Técnica |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Datos**       | Parquet unificado `sentencias_desnat.parquet` (~13,871 sentencias filtradas y anonimizadas) + embeddings precomputados `embeddings.npy` (float16) | Fusión automática incremental con datos recolectados por el scraper de Playwright. |
| **Retrieval**   | `hiiamsid/sentence_similarity_spanish_es` (SBERT español) · embed del resumen del usuario → top-3 por similitud coseno, filtrado por régimen vía DuckDB        | Consulta end-to-end < 300 ms |
| **Diagnóstico** | Scorecard determinístico (pesos fijos en un dict Python, ver §4) | Cero entrenamiento, 100% explicable |
| **Financiero**  | Módulo `liquidacion.py` con fórmulas de beneficios truncos de la actividad privada (CTS, Gratificación, Vacaciones, Bonif. 9%) + **Cálculo de Intereses Legales Laborales (DL 25920)** | Aritmética 100% exacta y auditable con corte por prescripción (Ley 27321). |
| **UI**          | Streamlit con gráfico de distribución de liquidación interactivo (`st.bar_chart`) e indicador de tasa de éxito histórica en DuckDB | Alta interacción y visualización ejecutiva del caso. |
| **PDF**         | `fpdf2` con desglose financiero detallado, enlaces clicables oficiales a las sentencias completas y disclaimer legal | Reporte profesional de 2 páginas. |

---

## 4 · Motor de Diagnóstico — Scorecard de Indicios de Laboralidad

Fundamento: **principio de primacía de la realidad** y presunción de laboralidad del art. 4 del TUO del DL 728 (prestación personal + remuneración + subordinación). Cada indicio proviene de los criterios de los jueces en las sentencias.

| Indicio (pregunta del wizard) | Elemento que acredita | Peso |
|---|---|:---:|
| ¿Cumplías un horario fijo impuesto por la entidad? | Subordinación | **20** |
| ¿Tenías un jefe directo que te daba órdenes y supervisaba? | Subordinación | **20** |
| ¿Marcabas asistencia (fotocheck, biométrico, cuaderno)? | Subordinación | **15** |
| ¿Usabas herramientas/equipos/correo del empleador? | Ajenidad | **10** |
| ¿Recibiste memos, sanciones o llamadas de atención? | Poder disciplinario | **10** |
| ¿Emitías recibos correlativos todos los meses por monto similar? | Remuneración periódica | **10** |
| ¿Trabajabas de forma personal (no podías delegar)? | Prestación personal | **10** |
| ¿Trabajaste en exclusiva para esa entidad? | Exclusividad (indicio) | **5** |

**Semáforo resultante** (suma 0–100):

- 🟢 **≥ 70 — Caso sólido**: concurren los tres elementos esenciales.
- 🟡 **40–69 — Caso con indicios**: requiere reforzar prueba de subordinación.
- 🔴 **< 40 — Caso débil**: predominan rasgos de autonomía real.

---

## 5 · Motor Financiero — Reglas por régimen

### Régimen privado (DL 728)

| Concepto | Base legal | Fórmula simplificada |
|---|---|---|
| **CTS** | DS 001-97-TR | `(sueldo + 1/6 gratif.) × (meses/12)` por periodo |
| **Gratificaciones** | Ley 27735 | `sueldo × 2` por año (jul + dic) + **9% bonif. extraordinaria** |
| **Vacaciones truncas** | DL 713 | `sueldo × (meses/12)` por año no gozado |
| **Intereses Laborales** | <mark>Decreto Ley 25920</mark> | Tasa promedio referencial (~3% anual) calculada desde el cese |
| **Prescripción** | <mark>Ley 27321</mark> | Corte automático a 4 años desde el cese |

### Régimen público (Ley 24041 / DL 276)
*   Consecuencia principal: **Reincorporación laboral** (estabilidad), no liquidación monetaria.
*   **Bloque Huatuco** automático: advierte que la reposición exige plaza vacante y presupuesto de ingreso por concurso, con la salvedad de **obreros municipales** y personal de confianza.

### Régimen CAS (DL 1057)
*   Desnaturalización de locación a CAS: orienta a estabilidad laboral en la entidad pública sujeta a las reglas del precedente Huatuco.

---

## 6 · Jurisprudencia de Soporte y Acceso al PDF Completo

*   **Búsqueda Semántica:** Se genera similitud coseno entre el texto de hechos y los resúmenes de sentencias con filtro en DuckDB.
*   **Presentación Clara:** Se traduce el resultado del juicio a lenguaje ciudadano (ej. *"A FAVOR DEL TRABAJADOR"*), se limpia el extracto de números o tecnicismos judiciales al inicio y se ocultan pretensiones que exponen nombres propios.

---

## 7 · Scraper de Expansión de Conocimiento (`src/scraper_boil.py`)
Implementado con **Playwright** en Python. Funciona de manera asistida/headed:
1. Abre de forma visible el portal de jurisprudencia del Tribunal Constitucional del Perú.
2. Permite al usuario resolver CAPTCHAs y configurar filtros de búsqueda libremente.
3. Al presionar ENTER en consola, captura de forma automatizada los resultados visibles (títulos, links oficiales y sumillas) y los guarda en `data/nuevas_sentencias_tc.json`, listos para ser fusionados de forma incremental mediante el pipeline de datos.

---

## 8 · Acceso y Descarga de Expedientes Completos (PDF Oficial)
Una de las funcionalidades más innovadoras para blindar el valor de la demo es la capacidad de **descargar el expediente judicial completo** de cada caso recomendado:
*   **Origen del Dato:** La base de datos asocia cada extracto de sentencia a su respectivo `url_pdf` oficial de la base del Poder Judicial o del Tribunal Constitucional (resoluciones con firma digitalizada).
*   **UI Interactiva (Streamlit):** Cada tarjeta de jurisprudencia incluye un enlace de navegación directa: `📄 Ver/Descargar Expediente Completo (PDF Oficial) ↗️` que abre la sentencia original.
*   **Enlace de Impresión (PDF):** En el reporte PDF descargable, los títulos de las sentencias son hipervínculos cliqueables e incorporan la etiqueta explícita `-> Clic aquí para ver/descargar la Sentencia Completa (PDF Oficial)`. Esto permite que el reporte impreso o digital sea una herramienta totalmente accionable para presentar ante SUNAFIL o un abogado.

---

## 9 · Explicación del Caso Asistida por IA (Gemini 2.5 Flash)
Para simplificar la asimilación del diagnóstico por parte del usuario, integramos **Inteligencia Artificial Generativa**:
*   **Integración de la API:** El usuario puede ingresar su clave de API de Google AI Studio en la barra lateral izquierda del panel de Streamlit de forma segura (sin filtración al historial de chat).
*   **Generación de Análisis y Sugerencias:** `src/explicador.py` envía la información estructurada del diagnóstico de solidez, el desglose numérico de capital e intereses devengados, y los precedentes jurisprudenciales recomendados a un modelo `gemini-2.5-flash` para que genere en lenguaje natural un reporte estructurado que explica qué significan los números del cálculo, de qué manera el precedente del Poder Judicial apoya su caso y cuáles son los pasos recomendados (reunir pruebas, ir a SUNAFIL, etc.).
