# ⚖️ MiLiqui (DesnaturalizaCheck 2.0)

> **De "buscador de casos" a "el único que te dice si la ley en la que se para tu caso todavía existe".**
> Diagnóstico inteligente de desnaturalización de contratos laborales y cálculo de beneficios sociales para trabajadores de Perú.

MiLiqui es una plataforma diseñada para hackathons que ayuda a locadores de servicios y trabajadores bajo regímenes CAS o informales a diagnosticar si su relación laboral fue encubierta bajo una simulación civil (desnaturalización de contrato) aplicando el **Principio de Primacía de la Realidad**.

---

## 🚀 Características Clave

1. **Diagnóstico e Indicios (Scorecard):** Evalúa el nivel de solidez jurídica de la desnaturalización mediante indicios clave (control de horario, subordinación, exclusividad, etc.).
2. **Cálculo de Beneficios Sociales (Liquidación):** Estima el monto total de beneficios adeudados para el régimen privado (DL 728), desglosando:
   - CTS Reclamable
   - Gratificaciones Truncas
   - Vacaciones No Gozadas / Truncas
   - Bonificación Extraordinaria (9%)
   - Interés Legal Laboral (DL 25920) acumulado automáticamente
3. **Búsqueda Semántica de Precedentes (SBERT):** Recupera los 3 fallos judiciales más similares a los hechos del usuario a partir de un corpus filtrado de 2,386 sentencias reales utilizando embeddings vectoriales en español (`hiiamsid/sentence_similarity_spanish_es`).
4. **Trazabilidad y Semáforo de Vigencia (El Peruano):** Compara las leyes que sustentan el fallo contra las fechas del diario oficial El Peruano para advertir mediante un semáforo (🟢 Vigente, 🟡 Modificada, 🔴 Derogada) si el precedente sigue siendo válido legalmente hoy en día.
5. **Visor de Expedientes Interactivo (Drawer):** Un panel lateral deslizable que permite leer el resumen judicial sobre un folio físico simulado con **resaltado inteligente inline** de indicios clave (horario, subordinación, honorarios, etc.) y tooltips descriptivos.
6. **Análisis Inteligente por IA (Gemini):** Genera una explicación estructurada en formato JSON para el usuario con un resumen empático, significado legal de los resultados y un plan de acción sugerido a modo de línea de tiempo.
7. **Exportación a PDF:** Genera un reporte formal y descargable con el desglose del diagnóstico, cálculo financiero y jurisprudencia relevante.

---

## 🛠️ Stack Tecnológico

### Backend (FastAPI)
- **FastAPI / Uvicorn:** Framework asíncrono de alto rendimiento.
- **DuckDB:** Base de datos analítica en memoria para búsquedas cruzadas rápidas de leyes y sentencias.
- **SBERT (SentenceTransformers):** Generación de embeddings en español para la búsqueda semántica.
- **Google GenAI (Gemini 2.5 Flash):** Resumen inteligente y empático estructurado en JSON.
- **FPDF2:** Generador de reportes formales en formato PDF.

### Frontend (React)
- **React 19 & Vite:** Entorno de compilación ultra rápido.
- **TailwindCSS 4.x:** Framework de estilos utilitarios modernos para la UI/UX premium oscura.

### Servidor y Despliegue (Docker)
- **Multi-stage Dockerfile:** Compila los recursos estáticos de React y los sirve con un reverse proxy en Nginx redireccionando la API `/api/*` al backend de forma segura y libre de CORS.

---

## 📁 Estructura de Datos (Bajo la capota)
El proyecto utiliza bases de datos analíticas optimizadas en formato Parquet:
* `sentencias_desnat.parquet` - 2,386 sentencias judiciales filtradas por desnaturalización.
* `embeddings.npy` - Vectores semánticos SBERT de las sentencias alinedos.
* `normas_sumillas_limpias.parquet` - 15 leyes laborales núcleo en la base de datos de El Peruano.
* `articulos_segmentados.parquet` - Texto completo artículo por artículo de las leyes.
* `editora_consolidado.parquet` - Registro histórico de vigencia, modificaciones y derogaciones de normas de El Peruano.

---

## 💻 Configuración Local

### Prerrequisitos
- Python 3.11+
- Node.js v20+
- pnpm (recomendado)

### 1. Iniciar el Backend
Desde la raíz del proyecto:
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el backend (puerto 8000)
python main.py
```

### 2. Iniciar el Frontend
Desde la carpeta `frontend/`:
```bash
# Copiar dependencias (si están en caché o localmente) e instalar
pnpm install

# Lanzar el servidor de desarrollo Vite (puerto 5173 con proxy para la API en puerto 8000)
npx vite
```

---

## ☁️ Despliegue en Producción (ej. Railway)

El despliegue en Railway utiliza el archivo `docker-compose.yml` que empaqueta automáticamente el backend y el frontend. 

1. Conecta tu repositorio de GitHub a **Railway**.
2. Railway detectará la arquitectura multi-contenedor.
3. Asegúrate de configurar la siguiente **Variable de Envtorno (Environment Variable)** en el panel de control del servicio de backend:
   - `GEMINI_API_KEY`: Tu clave de API de Google Gemini (obtenida gratis en Google AI Studio).
4. Railway asignará la URL pública HTTPS de forma automática al frontend de Nginx en el puerto 80.
