import os
import json
import google.generativeai as genai
from typing import Any, List, Dict

def explicar_caso(
    api_key: str, 
    datos_usuario: Dict[str, Any], 
    scorecard: Dict[str, Any], 
    liquidacion: Any, 
    sentencias: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Utiliza la API de Gemini para generar una explicación amigable, clara y empática 
    de los resultados del caso para el trabajador en un formato estructurado JSON.
    """
    if not api_key:
        return {
            "resumen": "Clave API de Gemini no configurada.",
            "significado": "Para recibir un análisis de tu caso impulsado por Inteligencia Artificial, ingresa tu API Key de Gemini en el panel lateral.",
            "analisis_detalle": "La IA te ayudará a interpretar el cálculo de la liquidación, el nivel de desnaturalización y cómo prepararte para un reclamo.",
            "pasos_sugeridos": [
                "Obtén una clave de API gratuita en Google AI Studio.",
                "Pega tu clave en el campo de la barra lateral de esta aplicación.",
                "Vuelve a presionar 'Calcular Diagnóstico' para ver los resultados."
            ]
        }
        
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
        Debes responder ÚNICAMENTE con un objeto JSON que siga estrictamente este esquema:
        {
          "resumen": "Resumen directo de una sola línea muy empático sobre su caso (ej. 'Tienes un caso muy sólido para reclamar tu liquidación e intereses').",
          "significado": "Explicación clara en palabras sencillas de qué significa el puntaje de indicios y su situación legal (máximo 4 oraciones).",
          "analisis_detalle": "Explicación amigable de los conceptos reclamables (CTS, gratificación, vacaciones, intereses) o de los derechos a reincorporación y estabilidad laboral según el régimen (máximo 5 oraciones).",
          "pasos_sugeridos": [
            "Paso 1 detallado",
            "Paso 2 detallado",
            "Paso 3 detallado"
          ]
        }
        """
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Intentar parsear el JSON generado
        parsed_data = json.loads(response.text)
        return parsed_data
        
    except Exception as e:
        return {
            "resumen": "Error al procesar la explicación del caso.",
            "significado": "Hubo una dificultad al conectar o procesar la respuesta de la Inteligencia Artificial.",
            "analisis_detalle": f"Detalle técnico del error: {str(e)}",
            "pasos_sugeridos": [
                "Verifica que tu clave API de Gemini sea válida y esté activa.",
                "Revisa tu conexión a internet e inténtalo nuevamente.",
                "Si el problema persiste, puedes guiarte de las sentencias y liquidación calculadas arriba."
            ]
        }
