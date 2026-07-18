import os
import google.generativeai as genai
from typing import Any, List, Dict

def explicar_caso(
    api_key: str, 
    datos_usuario: Dict[str, Any], 
    scorecard: Dict[str, Any], 
    liquidacion: Any, 
    sentencias: List[Dict[str, Any]]
) -> str:
    """
    Utiliza la API de Gemini para generar una explicación amigable, clara y empática 
    de los resultados del caso para el trabajador.
    """
    # Usar variable de entorno si no se recibe api_key por argumento
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
    if not api_key:
        return "Para ver una explicación personalizada por Inteligencia Artificial, ingresa tu API Key de Gemini en la barra lateral o confígurala como variable de entorno GEMINI_API_KEY."
        
    try:
        genai.configure(api_key=api_key)
        # Usamos gemini-2.5-flash por ser el modelo por defecto, rápido y económico
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Eres un abogado laboralista peruano muy empático y claro. Explícale a un trabajador el resultado de su análisis de desnaturalización de contrato de forma muy sencilla y cotidiana, sin tecnicismos complejos.
        
        Datos del Caso:
        - Régimen seleccionado: {datos_usuario['regimen']}
        - Tiempo laborado: Del {datos_usuario['fecha_inicio']} al {datos_usuario['fecha_cese']}
        - Sueldo mensual: S/ {datos_usuario['sueldo']:.2f}
        - Resumen de hechos: {datos_usuario['resumen_hechos']}
        
        Diagnóstico de Solidez:
        - Puntaje de Indicios: {scorecard['puntaje']}/100 ({scorecard['categoria']})
        """
        
        if liquidacion:
            prompt += f"""
            Resultados Económicos (Liquidación Estimada):
            - CTS Reclamable: S/ {liquidacion.cts_reclamable:.2f}
            - Gratificaciones Reclamables: S/ {liquidacion.gratif_reclamable:.2f}
            - Vacaciones Reclamables: S/ {liquidacion.vac_reclamable:.2f}
            - Bonificación 9%: S/ {liquidacion.bonif_reclamable:.2f}
            - Interés Legal Laboral (DL 25920): S/ {liquidacion.interes_reclamable:.2f}
            - TOTAL RECLAMABLE ESTIMADO: S/ {liquidacion.total_reclamable:.2f}
            - Total Prescrito (Perdido por el paso del tiempo): S/ {liquidacion.total_prescrito:.2f}
            """
        else:
            prompt += "\n- Consecuencia Principal: Reincorporación al puesto de trabajo (estabilidad laboral)."
            if datos_usuario.get('es_obrero_municipal'):
                prompt += "\n- Obrero Municipal: Cuenta con la excepción al precedente Huatuco, facilitando su reincorporación."
                
        prompt += "\n\nPrecedentes de jurisprudencia similares encontrados:\n"
        for i, s in enumerate(sentencias):
            prompt += f"- {s['titulo']} (Similitud: {s.get('similitud', 0)*100:.1f}%) - Sumilla: {s['abstract'][:250]}\n"
            
        prompt += """
        Escribe un resumen analítico estructurado en 3 secciones cortas usando Markdown:
        1. **¿Qué significa esto para ti?**: Explica el diagnóstico de solidez y tu situación legal en palabras simples.
        2. **Análisis de tu dinero/situación**: Si hay liquidación, explica de forma amigable qué es cada concepto (CTS, gratificación, etc.) y por qué se sumaron intereses. Si es régimen público, aclara el tema de la reincorporación y la estabilidad.
        3. **Pasos sugeridos a seguir**: Recomienda acciones concretas (como reunir correos, ir a SUNAFIL para una conciliación gratuita o buscar asistencia legal formal).
        
        Mantén un tono empático, tranquilizador y muy profesional.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error al generar la explicación con IA: {e}"
