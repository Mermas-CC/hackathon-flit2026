from fpdf import FPDF
import datetime
from typing import Dict, Any, List

class ReportePDF(FPDF):
    def header(self):
        # Título
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(26, 54, 93) # Navy blue
        self.cell(0, 10, 'DesnaturalizaCheck - Reporte Legal & Financiero', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(113, 128, 150)
        self.cell(0, 5, 'Diagnostico de Laboralidad y Calculo de Beneficios Sociales', 0, 1, 'C')
        self.ln(5)
        # Línea de separación
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(160, 174, 192)
        # Paginación
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def clean_txt(text: str) -> str:
    """Reemplaza tildes y caracteres no soportados por Helvetica latin-1 de fpdf2"""
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U',
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '⚖️': '', '🟢': '', '🟡': '', '🔴': '', '⚠️': '', '✅': '', '💡': ''
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

def generar_pdf_reporte(
    datos_usuario: Dict[str, Any],
    scorecard: Dict[str, Any],
    liquidacion: Any, # DetalleLiquidacion
    sentencias: List[Dict[str, Any]],
    output_path: str
):
    pdf = ReportePDF()
    pdf.add_page()
    
    # 1. Resumen Informativo
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(45, 55, 72)
    pdf.cell(0, 8, clean_txt('1. RESUMEN DEL CASO'), 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(50, 6, clean_txt('Regimen Laboral:'), 0, 0)
    pdf.cell(0, 6, clean_txt(datos_usuario['regimen']), 0, 1)
    pdf.cell(50, 6, clean_txt('Fecha de Inicio:'), 0, 0)
    pdf.cell(0, 6, clean_txt(str(datos_usuario['fecha_inicio'])), 0, 1)
    pdf.cell(50, 6, clean_txt('Fecha de Cese:'), 0, 0)
    pdf.cell(0, 6, clean_txt(str(datos_usuario['fecha_cese'])), 0, 1)
    pdf.cell(50, 6, clean_txt('Remuneracion Mensual:'), 0, 0)
    pdf.cell(0, 6, clean_txt(f"S/ {datos_usuario['sueldo']:.2f}"), 0, 1)
    pdf.ln(5)
    
    # 2. Diagnóstico de Laboralidad
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, clean_txt('2. DIAGNOSTICO DE SOLIDEREZ DEL CASO'), 0, 1)
    pdf.set_font('Helvetica', '', 10)
    
    puntaje = scorecard['puntaje']
    semaforo = scorecard['semaforo'] # '🟢', '🟡', '🔴'
    categoria = scorecard['categoria'] # 'Caso Solido', 'Caso con indicios', 'Caso Debil'
    
    pdf.cell(50, 6, clean_txt('Indice de Solidez:'), 0, 0)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 6, clean_txt(f"{puntaje}/100 - {categoria}"), 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, clean_txt(scorecard['explicacion']))
    pdf.ln(5)
    
    # 3. Liquidación de Beneficios (sólo si es DL 728)
    if datos_usuario['regimen'] == 'Privado (DL 728)':
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, clean_txt('3. CALCULO ESTIMADO DE BENEFICIOS SOCIALES (DL 728)'), 0, 1)
        pdf.set_font('Helvetica', 'B', 10)
        
        # Tabla de Liquidación
        # Encabezado
        pdf.set_fill_color(247, 250, 252)
        pdf.cell(60, 8, clean_txt('Concepto'), 1, 0, 'L', True)
        pdf.cell(65, 8, clean_txt('Monto Reclamable'), 1, 0, 'R', True)
        pdf.cell(65, 8, clean_txt('Monto Prescrito'), 1, 1, 'R', True)
        
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(60, 7, clean_txt('CTS (Compensacion de Tiempo de Servicios)'), 1, 0)
        pdf.cell(65, 7, f"S/ {liquidacion.cts_reclamable:.2f}", 1, 0, 'R')
        pdf.cell(65, 7, f"S/ {liquidacion.cts_prescrito:.2f}", 1, 1, 'R')
        
        pdf.cell(60, 7, clean_txt('Gratificaciones (Julio y Diciembre)'), 1, 0)
        pdf.cell(65, 7, f"S/ {liquidacion.gratif_reclamable:.2f}", 1, 0, 'R')
        pdf.cell(65, 7, f"S/ {liquidacion.gratif_prescrito:.2f}", 1, 1, 'R')
        
        pdf.cell(60, 7, clean_txt('Vacaciones Truncas / No Gozadas'), 1, 0)
        pdf.cell(65, 7, f"S/ {liquidacion.vac_reclamable:.2f}", 1, 0, 'R')
        pdf.cell(65, 7, f"S/ {liquidacion.vac_prescrito:.2f}", 1, 1, 'R')
        
        pdf.cell(60, 7, clean_txt('Bonificacion Extraordinaria (9%)'), 1, 0)
        pdf.cell(65, 7, f"S/ {liquidacion.bonif_reclamable:.2f}", 1, 0, 'R')
        pdf.cell(65, 7, f"S/ {liquidacion.bonif_prescrito:.2f}", 1, 1, 'R')
        
        pdf.cell(60, 7, clean_txt('Interes Legal Laboral (DL 25920)'), 1, 0)
        pdf.cell(65, 7, f"S/ {liquidacion.interes_reclamable:.2f}", 1, 0, 'R')
        pdf.cell(65, 7, f"S/ {liquidacion.interes_prescrito:.2f}", 1, 1, 'R')
        
        # Totales
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_fill_color(237, 242, 247)
        pdf.cell(60, 8, clean_txt('TOTAL ESTIMADO'), 1, 0, 'L', True)
        pdf.cell(65, 8, f"S/ {liquidacion.total_reclamable:.2f}", 1, 0, 'R', True)
        pdf.cell(65, 8, f"S/ {liquidacion.total_prescrito:.2f}", 1, 1, 'R', True)
        pdf.ln(5)
        
        if liquidacion.prescrito_totalmente:
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(229, 62, 62)
            pdf.multi_cell(0, 5, clean_txt("ALERTA DE PRESCRIPCION: Han transcurrido mas de 4 anos desde el cese laboral (Ley 27321). Toda accion de cobro podria ser declarada prescrita judicialmente."))
            pdf.set_text_color(45, 55, 72)
            pdf.ln(5)
    elif datos_usuario['regimen'] == 'Público (Ley 24041 / DL 276)':
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, clean_txt('3. ORIENTACION DE REGIMEN PUBLICO (Ley 24041)'), 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, clean_txt("La desnaturalizacion en el Sector Publico no otorga beneficios del regimen 728. Otorga derecho a la reincorporacion laboral."))
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.multi_cell(0, 5, clean_txt("Advertencia Huatuco (Cas. 5057-2013-Junin): Exige concurso publico de meritos en plaza vacante presupuestada para la reincorporacion indefinida."))
        pdf.ln(5)
    else:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, clean_txt('3. ORIENTACION DE REGIMEN CAS (DL 1057)'), 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 5, clean_txt("El regimen CAS otorga estabilidad laboral relativa y la posibilidad de reposicion en caso de despido arbitrario segun jurisprudencia vinculante."))
        pdf.ln(5)
        
    # 4. Jurisprudencia de Soporte
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, clean_txt('4. JURISPRUDENCIA DE SOPORTE (TOP-3 PRECEDENTES)'), 0, 1)
    
    import re
    
    for i, sent in enumerate(sentencias):
        titulo_raw = sent['titulo']
        
        # Determinar el sentido del fallo de forma amigable
        fallo_amigable = "Fallo no especificado"
        if "Fundada" in titulo_raw:
            fallo_amigable = "GANO EL TRABAJADOR (Demanda Fundada)"
        elif "Infundada" in titulo_raw:
            fallo_amigable = "GANO EL EMPLEADOR (Demanda Infundada)"
        elif "Improcedente" in titulo_raw:
            fallo_amigable = "Improcedente (Rechazo formal)"
            
        # Extraer el numero de expediente o casacion
        exp_match = re.search(r'(\d+-\d{4})', titulo_raw)
        expediente = f"Expediente N. {exp_match.group(1)}" if exp_match else titulo_raw
        
        # Limpiar parrafos y numeros iniciales de la sumilla
        abstract_limpio = sent['abstract'].strip()
        abstract_limpio = re.sub(r'^\d+\.\s*(?:Que\s+)?', '', abstract_limpio) # Quitar "9. Que..."
        abstract_limpio = abstract_limpio[0].upper() + abstract_limpio[1:] if abstract_limpio else ""
        
        pdf.set_font('Helvetica', 'B', 10)
        url_sentencia = sent.get('url', '')
        pdf.cell(0, 6, clean_txt(f"Caso {i+1}: {expediente} (Similitud: {sent['similitud']*100:.1f}%)"), 0, 1, link=url_sentencia)
        
        # Enlace de descarga oficial
        if url_sentencia:
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(49, 130, 206) # Azul
            pdf.cell(0, 4, clean_txt("-> Clic aqui para ver/descargar la Sentencia Completa (PDF Oficial)"), 0, 1, link=url_sentencia)
            pdf.set_text_color(45, 55, 72)
            
        # Sentido del fallo resaltado
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(31, 82, 222) if "GANO EL TRABAJADOR" in fallo_amigable else pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 5, clean_txt(f"Resultado del Juicio: {fallo_amigable}"), 0, 1)
        pdf.set_text_color(45, 55, 72)
        
        # Abstract amigable
        pdf.set_font('Helvetica', '', 9)
        pdf.multi_cell(0, 4, clean_txt(abstract_limpio[:320] + "..."))
        pdf.ln(3)
        
    # 5. Disclaimer Legal
    pdf.ln(5)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(113, 128, 150)
    pdf.multi_cell(0, 4, clean_txt("DISCLAIMER: Esta es una herramienta de orientacion algoritmica y no constituye asesoria legal formal. Los calculos y analisis de solidez son referenciales y se basan en criterios jurisprudenciales generales. Para iniciar acciones legales o administrativas, se aconseja consultar con un abogado laboralista o acudir a SUNAFIL."))
    
    pdf.output(output_path)
