import os
import sys
import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Asegurar que el directorio raíz sea importable
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

from src.liquidacion import calcular_liquidacion_728, obtener_mensaje_regimen_publico, obtener_mensaje_cas
from src.retrieval import SentenciasRetrieval
from src.elperuano_manager import ElPeruanoManager
from src.explicador import explicar_caso
from src.pdf_generator import generar_pdf_reporte

app = FastAPI(title="DesnaturalizaCheck API", version="2.0")

# Habilitar CORS para permitir peticiones desde React (Vite corre por defecto en 5173 o 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción acotar al host específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar managers del backend
retriever = SentenciasRetrieval()
elperuano = ElPeruanoManager()

# Modelos Pydantic para validación de datos
class DiagnosticoRequest(BaseModel):
    regimen: str
    fecha_inicio: str
    fecha_cese: str
    sueldo: float
    resumen_hechos: str
    es_obrero_municipal: bool
    respuestas_scorecard: Dict[str, str]
    dias_vacaciones_tomadas: Optional[int] = 0
    cts_ya_pagada: Optional[float] = 0.0
    gratif_ya_pagada: Optional[float] = 0.0

class ExplicacionRequest(BaseModel):
    api_key: str
    datos_usuario: Dict[str, Any]
    scorecard_info: Dict[str, Any]
    liquidacion: Optional[Dict[str, Any]] = None
    sentencias: List[Dict[str, Any]]

class PdfRequest(BaseModel):
    datos_usuario: Dict[str, Any]
    scorecard_info: Dict[str, Any]
    liquidacion: Optional[Dict[str, Any]] = None
    sentencias: List[Dict[str, Any]]

# Helper para convertir strings ISO a objetos datetime.date
def parse_date(date_str: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido. Usar YYYY-MM-DD: {e}")

@app.post("/api/diagnostico")
def procesar_diagnostico(req: DiagnosticoRequest):
    f_inicio = parse_date(req.fecha_inicio)
    f_cese = parse_date(req.fecha_cese)
    
    if f_inicio > f_cese:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la de cese.")
    
    # 1. Calcular Scorecard de Solidez
    preguntas_pesos = {
        "horario": 20, "jefe": 20, "asistencia": 15, "herramientas": 10,
        "memos": 10, "recibos": 10, "personal": 10, "exclusividad": 5
    }
    
    puntaje = 0
    for key, val in req.respuestas_scorecard.items():
        if val == "Sí":
            puntaje += preguntas_pesos.get(key, 0)
            
    if puntaje >= 70:
        semaforo = "🟢"
        categoria = "Caso Altamente Sólido"
        explicacion = (
            "Existen indicios concurrentes y muy fuertes de que tu relación con la empresa fue de carácter subordinado (laboral) "
            "y no civil. Bajo el Principio de Primacía de la Realidad, tienes bases legales sumamente sólidas para demandar."
        )
    elif puntaje >= 40:
        semaforo = "🟡"
        categoria = "Caso con Indicios Moderados"
        explicacion = (
            "Se detectan indicios significativos de laboralidad. Para un proceso exitoso, es clave recopilar más pruebas "
            "asociadas a la subordinación directa (correos, mensajes de WhatsApp, etc.)."
        )
    else:
        semaforo = "🔴"
        categoria = "Caso con Indicios Débiles"
        explicacion = (
            "Los indicios de laboralidad son limitados. La relación se asemeja más a una locación de servicios autónoma real."
        )
        
    scorecard_info = {
        "puntaje": puntaje,
        "semaforo": semaforo,
        "categoria": categoria,
        "explicacion": explicacion
    }
    
    # 2. Calcular Liquidación Financiera
    liq_res = None
    info_publico = None
    
    if req.regimen == 'Privado (DL 728)':
        liq = calcular_liquidacion_728(
            f_inicio, 
            f_cese, 
            req.sueldo,
            dias_vacaciones_tomadas=req.dias_vacaciones_tomadas or 0,
            cts_ya_pagada=req.cts_ya_pagada or 0.0,
            gratif_ya_pagada=req.gratif_ya_pagada or 0.0
        )
        liq_res = {
            "meses_totales": liq.meses_totales,
            "dias_totales": liq.dias_totales,
            "prescrito_totalmente": liq.prescrito_totalmente,
            "cts_reclamable": liq.cts_reclamable,
            "gratif_reclamable": liq.gratif_reclamable,
            "vac_reclamable": liq.vac_reclamable,
            "bonif_reclamable": liq.bonif_reclamable,
            "interes_reclamable": liq.interes_reclamable,
            "total_reclamable": liq.total_reclamable,
            "cts_prescrito": liq.cts_prescrito,
            "gratif_prescrito": liq.gratif_prescrito,
            "vac_prescrito": liq.vac_prescrito,
            "bonif_prescrito": liq.bonif_prescrito,
            "interes_prescrito": liq.interes_prescrito,
            "total_prescrito": liq.total_prescrito
        }
    elif req.regimen == 'Público (Ley 24041 / DL 276)':
        info_publico = obtener_mensaje_regimen_publico(req.es_obrero_municipal)
    else:
        info_publico = obtener_mensaje_cas()
        
    # 3. Recuperar Jurisprudencia Relacionada
    sentencias = []
    try:
        raw_sents = retriever.search(req.resumen_hechos, req.regimen, top_k=3)
        for s in raw_sents:
            norma_ref = s.get('norma_derecho', 'Ley 24041')
            
            # Enriquecimiento y Verificación de Vigencia con El Peruano
            articulo_info = elperuano.obtener_articulo_por_ley(norma_ref)
            vigencia_info = elperuano.verificar_vigencia(norma_ref, s.get('fecha', '2020-01-01'))
            
            sentencias.append({
                "id": s['id'],
                "titulo": s['titulo'],
                "abstract": s['abstract'],
                "pretension": s['pretension'],
                "similitud": s['similitud'],
                "url": s['url'],
                "norma_derecho": norma_ref,
                "fecha": s['fecha'],
                "articulo_info": articulo_info,
                "vigencia_info": vigencia_info
            })
    except Exception as e:
        print(f"Error al recuperar jurisprudencia: {e}")
        
    # 4. Obtener Estadística Histórica
    total_casos = 0
    tasa_exito = 0.0
    try:
        stats = retriever.con.execute(f"""
            SELECT count(*), 
                   sum(case when titulo like '%Fundada%' then 1 else 0 end) as fundadas 
            FROM sentencias 
            WHERE regimen = '{req.regimen}'
        """).fetchone()
        if stats and stats[0] > 0:
            total_casos = stats[0]
            fundadas = stats[1] if stats[1] else 0
            tasa_exito = (fundadas / total_casos * 100)
    except Exception as e:
        print(f"Error al calcular estadísticas: {e}")
        
    return {
        "scorecard": scorecard_info,
        "liquidacion": liq_res,
        "info_publico": info_publico,
        "sentencias": sentencias,
        "stats": {
            "total_casos": total_casos,
            "tasa_exito": round(tasa_exito, 1)
        }
    }

@app.post("/api/explicar-ia")
def procesar_explicacion_ia(req: ExplicacionRequest):
    # Formatear la liquidación a un objeto simulado compatible
    class MockLiquidacion:
        def __init__(self, d):
            self.cts_reclamable = d.get('cts_reclamable', 0.0)
            self.gratif_reclamable = d.get('gratif_reclamable', 0.0)
            self.vac_reclamable = d.get('vac_reclamable', 0.0)
            self.bonif_reclamable = d.get('bonif_reclamable', 0.0)
            self.interes_reclamable = d.get('interes_reclamable', 0.0)
            self.total_reclamable = d.get('total_reclamable', 0.0)
            self.total_prescrito = d.get('total_prescrito', 0.0)
            
    liq_obj = MockLiquidacion(req.liquidacion) if req.liquidacion else None
    
    explicacion = explicar_caso(
        api_key=req.api_key,
        datos_usuario=req.datos_usuario,
        scorecard=req.scorecard_info,
        liquidacion=liq_obj,
        sentencias=req.sentencias
    )
    return {"explicacion": explicacion}

@app.post("/api/reporte-pdf")
def descargar_reporte_pdf(req: PdfRequest):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "data", "reporte_caso.pdf")
    
    # Formatear liquidación compatible
    class MockLiquidacion:
        def __init__(self, d):
            self.cts_reclamable = d.get('cts_reclamable', 0.0)
            self.gratif_reclamable = d.get('gratif_reclamable', 0.0)
            self.vac_reclamable = d.get('vac_reclamable', 0.0)
            self.bonif_reclamable = d.get('bonif_reclamable', 0.0)
            self.interes_reclamable = d.get('interes_reclamable', 0.0)
            self.total_reclamable = d.get('total_reclamable', 0.0)
            self.total_prescrito = d.get('total_prescrito', 0.0)
            self.cts_prescrito = d.get('cts_prescrito', 0.0)
            self.gratif_prescrito = d.get('gratif_prescrito', 0.0)
            self.vac_prescrito = d.get('vac_prescrito', 0.0)
            self.bonif_prescrito = d.get('bonif_prescrito', 0.0)
            self.interes_prescrito = d.get('interes_prescrito', 0.0)
            self.meses_totales = d.get('meses_totales', 0)
            self.dias_totales = d.get('dias_totales', 0)
            self.prescrito_totalmente = d.get('prescrito_totalmente', False)
            
    liq_obj = MockLiquidacion(req.liquidacion) if req.liquidacion else None
    
    # Adecuar formato fechas para pdf_generator
    datos_pdf = {
        'regimen': req.datos_usuario['regimen'],
        'fecha_inicio': parse_date(req.datos_usuario['fecha_inicio']),
        'fecha_cese': parse_date(req.datos_usuario['fecha_cese']),
        'sueldo': req.datos_usuario['sueldo'],
        'resumen_hechos': req.datos_usuario['resumen_hechos'],
        'es_obrero_municipal': req.datos_usuario.get('es_obrero_municipal', False),
        'dias_vacaciones_tomadas': req.datos_usuario.get('dias_vacaciones_tomadas', 0),
        'cts_ya_pagada': req.datos_usuario.get('cts_ya_pagada', 0.0),
        'gratif_ya_pagada': req.datos_usuario.get('gratif_ya_pagada', 0.0)
    }
    
    try:
        generar_pdf_reporte(
            datos_pdf,
            req.scorecard_info,
            liq_obj,
            req.sentencias,
            pdf_path
        )
        if os.path.exists(pdf_path):
            return FileResponse(pdf_path, media_type="application/pdf", filename="Reporte_Desnaturalizacion.pdf")
        else:
            raise HTTPException(status_code=500, detail="El archivo PDF no pudo ser creado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {e}")

@app.post("/api/analizar-boleta")
async def analizar_boleta(
    file: UploadFile = File(...),
    api_key: str = Form(...)
):
    import google.generativeai as genai
    import json
    
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo subido debe ser una imagen.")
        
    try:
        # Configurar la API Key
        genai.configure(api_key=api_key)
        
        # Cargar los bytes de la imagen
        image_bytes = await file.read()
        image_data = {
            "mime_type": file.content_type,
            "data": image_bytes
        }
        
        prompt = """
        Analiza la imagen adjunta de esta boleta de pago, recibo por honorarios o documento de liquidación de beneficios sociales de Perú.
        Extrae la información relevante y devuélvela estrictamente en formato JSON válido.
        Los campos que debes extraer son (si no los encuentras o no existen, devuélvelos como null o 0):
        - sueldo: (float) la remuneración mensual o básico
        - fecha_inicio: (string en formato YYYY-MM-DD) fecha de ingreso o inicio de labores
        - fecha_cese: (string en formato YYYY-MM-DD) fecha de cese o término de labores
        - dias_vacaciones_tomadas: (int) días de vacaciones gozados que figuren en el documento
        - cts_ya_pagada: (float) monto de CTS depositado o pagado que figure en la boleta/liquidación
        - gratif_ya_pagada: (float) monto de gratificaciones pagadas que figure en la boleta/liquidación

        Devuelve exclusivamente el objeto JSON en texto plano, sin bloques de código markdown, sin prefijos ni comentarios.
        """
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([prompt, image_data])
        
        # Limpiar posibles bloques markdown del output de Gemini
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al analizar la boleta con Gemini IA: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
