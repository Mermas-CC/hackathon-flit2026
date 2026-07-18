# Brief Project Description: DesnaturalizaCheck v2.0
*Ficha descriptiva del proyecto para entregas y postulaciones*

---

## 🇪🇸 Descripción en Español

**Título del Proyecto:** DesnaturalizaCheck v2.0 — Asistente Legal y Calculadora Inteligente de Beneficios Sociales

### Resumen
**DesnaturalizaCheck v2.0** es una plataforma web inteligente diseñada para combatir la asimetría de información y el abuso laboral en el Perú. Permite a trabajadores contratados de manera encubierta bajo la modalidad civil de "Locación de Servicios" (Recibos por Honorarios) diagnosticar la solidez de su relación de dependencia real, y calcular con precisión matemática sus beneficios sociales no pagados (CTS, Gratificaciones, Vacaciones e Intereses Legales según el Decreto Ley 25920), deduciendo montos ya abonados parcialmente o días de vacaciones físicas gozados.

### Problema que resuelve
Las calculadoras laborales tradicionales son estáticas, "todo o nada", y no consideran el historial real del trabajador, ignorando deducciones, cálculo complejo de intereses acumulados o el límite de prescripción legal de 4 años (Ley 27321). Esto ocasiona que los trabajadores acepten liquidaciones informales muy por debajo de lo dictaminado por la ley laboral peruana.

### Principales Aportes e Innovación
1. **Calculadora Inteligente de Precisión:** Primer motor de liquidación peruano que permite deducir días de vacaciones tomados y CTS/Gratificaciones recibidas parcialmente, calculando en tiempo real montos reclamables vs. prescritos e intereses legales por cese.
2. **Auto-completado Multimodal por IA:** Mediante **Gemini 2.5 Flash**, el usuario puede subir una foto o captura de sus recibos o boletas, extrayendo automáticamente el sueldo, fechas y conceptos recibidos.
3. **Buscador Semántico de Jurisprudencia:** Vincula vectorialmente el caso del usuario con las 3 sentencias más relevantes de desnaturalización publicadas en **El Peruano** en tiempo real.
4. **Reporte Ejecutivo PDF:** Generación instantánea de una hoja de liquidación con diseño ejecutivo para negociaciones o denuncias ante SUNAFIL.

### Stack Tecnológico
* **Frontend:** React, Tailwind CSS v4 (con UI Glassmorphic simplificada y tarjetas interactivas).
* **Backend:** FastAPI (Python 3.11) optimizado con PyTorch CPU-only en contenedores Docker.
* **IA y Búsqueda:** Gemini 2.5 Flash, DuckDB Vector Search (Sentence Transformers).
* **Despliegue:** AWS EC2 & Docker Compose.

---

## 🇺🇸 English Description

**Project Title:** DesnaturalizaCheck v2.0 — Legal Assistant & Smart Social Benefits Calculator

### Summary
**DesnaturalizaCheck v2.0** is an intelligent web platform designed to reduce information asymmetry and labor abuse in Peru. It helps workers hired under masked "independent contractor" agreements (Locación de Servicios) diagnose the legal solidity of their employment relationship and calculate their unpaid social benefits (CTS, Gratifications, Vacations, and Legal Interest under DL 25920) with mathematical precision. The system automatically deducts partial payments and vacation days already taken.

### Problem Solved
Traditional labor calculators are static and binary. They ignore the worker's actual history (such as partial payments or vacation days taken), complex legal interest calculations, and the 4-year legal prescription limit (Ley 27321). This forces workers to accept informal, low-ball settlements.

### Key Contributions & Innovation
1. **Precision Financial Calculator:** The first Peruvian liquidations engine that dynamically deducts taken vacation days and partial payments, separating Claimable vs. Prescribed amounts, and computing interest.
2. **Multimodal AI Autocomplete:** Powered by **Gemini 2.5 Flash**, users upload photos of pay slips or receipts, and the AI automatically extracts base salaries, dates, and historical payouts.
3. **Semantic Precedent Finder:** Employs vector search in **DuckDB** to match the worker's case against the top 3 similar rulings from **El Peruano** in milliseconds.
4. **Executive PDF Export:** Instantly exports a beautifully designed peritaje sheet ready for labor ministry (SUNAFIL) conciliations.

### Tech Stack
* **Frontend:** React, Tailwind CSS v4.
* **Backend:** FastAPI, Docker (optimized CPU-only PyTorch).
* **AI & Search:** Gemini 2.5 Flash, DuckDB Vector Search.
* **Cloud:** AWS EC2 & Docker Compose.
