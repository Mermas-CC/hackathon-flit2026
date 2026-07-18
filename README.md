# MiLiqui

Estimacion de desnaturalizacion laboral y calculo de beneficios sociales para el mercado peruano.

MiLiqui evalua si una relacion de locacion de servicios o regimen CAS califica como relacion de dependencia encubierta (desnaturalizacion de contrato) mediante el Principio de Primacia de la Realidad. Compara el caso del usuario con resoluciones del Diario Oficial El Peruano y jurisprudencia del Poder Judicial, calculando el importe de la deuda laboral estimada.

---

## Componentes del Sistema

1. **Analisis de Indicios (Scorecard):** Cuestionario estructurado segun criterios vinculantes de la Corte Suprema para determinar la solidez del vinculo laboral (subordinacion, jornada y control directo).
2. **Calculo de Beneficios Sociales (Liquidacion):** Estima el monto adeudado bajo el regimen laboral de la actividad privada (DL 728) por concepto de:
   - Compensacion por Tiempo de Servicios (CTS).
   - Gratificaciones legales (Julio y Diciembre).
   - Vacaciones no gozadas o truncas.
   - Bonificacion extraordinaria (Ley 29351).
   - Interes legal laboral (DL 25920) devengado de forma diaria tras el cese.
   - Filtro de prescripcion de 4 anos segun la Ley 27321.
3. **Busqueda Semantica de Precedentes:** Recupera los 3 fallos judiciales de mayor similitud factica a partir de un corpus local de 2,386 sentencias reales, usando un modelo de embeddings en espanol (SBERT).
4. **Validacion de Vigencia Normativa:** Cruza los articulos y leyes citados en el fallo con la base del Diario Oficial El Peruano para identificar si la norma continua vigente o ha sido modificada/derogada.
5. **Visor de Folio Judicial:** Despliega el resumen de la sentencia en un formato de folio fisico, destacando de forma inline las marcas de indicios laborables identificados con notas explicativas.
6. **Sintesis por Inteligencia Artificial:** Gemini 2.5 Flash procesa el diagnostico para estructurar un JSON con la sintesis del caso, interpretacion de resultados y un plan de accion ordenado por pasos.
7. **Reporte Formal en PDF:** Generacion de un documento de diagnostico con la liquidacion de beneficios e historial de jurisprudencia ajustado a la paleta de colores de la aplicacion.

---

## Arquitectura y Datos

- **Base de Datos:** DuckDB en memoria para cruces analiticos de sentencias y vigencia.
- **Modelos de Lenguaje:** Gemini 2.5 Flash y SBERT (`hiiamsid/sentence_similarity_spanish_es`).
- **Backend:** FastAPI expuesto mediante Uvicorn.
- **Frontend:** React y TailwindCSS.
- **Estructura de Datos (data/):**
  - `sentencias_desnat.parquet` (2,386 sentencias procesadas).
  - `embeddings.npy` (vectores semanticos de sentencias).

---

## Ejecucion Local

### Requisitos
- Python 3.11 o superior.
- Node.js v20 o superior.

### 1. Servidor Backend
Desde el directorio raiz:
```bash
# Entorno virtual e instalacion
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Iniciar servidor (puerto 8000)
python main.py
```

### 2. Cliente Frontend
Desde el directorio `frontend/`:
```bash
# Instalacion de dependencias
pnpm install

# Iniciar servidor de desarrollo (puerto 5173 con proxy configurado al puerto 8000)
npx vite
```

---

## Despliegue (Docker / Railway)

La aplicacion esta configurada para desplegarse mediante contenedores multi-etapa usando el archivo `docker-compose.yml` de la raiz.

1. Conectar el repositorio en **Railway**.
2. Declarar la variable de entorno obligatoria:
   - `GEMINI_API_KEY`: Clave de acceso a Google AI Studio.
3. El frontend compila de forma estatica y Nginx sirve la web en el puerto 80 redireccionando las peticiones de `/api/*` al backend de FastAPI.
