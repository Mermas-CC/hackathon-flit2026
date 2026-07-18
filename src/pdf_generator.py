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
    
    # 1. Resumen Informativo (Diseñado como Tarjeta de Metadatos)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42) # Slate-900
    pdf.cell(0, 8, clean_txt('1. RESUMEN DEL CASO LABORAL'), 0, 1)
    
    pdf.set_fill_color(248, 250, 252) # Slate-50 bg
    pdf.set_draw_color(226, 232, 240) # Slate-200 border
    
    # Dibujar fondo rectangular para los datos generales
    pdf.rect(10, pdf.get_y(), 190, 48, 'F')
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105) # Slate-600
    
    # Columna 1
    pdf.set_xy(15, pdf.get_y() + 3)
    pdf.cell(45, 6, clean_txt('Regimen Laboral:'), 0, 0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 6, clean_txt(datos_usuario['regimen']), 0, 1)
    
    pdf.set_x(15)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(45, 6, clean_txt('Fecha de Inicio:'), 0, 0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 6, clean_txt(str(datos_usuario['fecha_inicio'])), 0, 1)
    
    pdf.set_x(15)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(45, 6, clean_txt('Fecha de Cese:'), 0, 0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 6, clean_txt(str(datos_usuario['fecha_cese'])), 0, 1)
    
    pdf.set_x(15)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(45, 6, clean_txt('Sueldo de Referencia:'), 0, 0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 6, clean_txt(f"S/ {datos_usuario['sueldo']:.2f}"), 0, 1)

    # Columna 2 (Deducciones y variables de personalización)
    # Volvemos arriba en la misma banda
    pdf.set_xy(110, pdf.get_y() - 24)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(45, 6, clean_txt('Vacaciones Gozadas:'), 0, 0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 6, clean_txt(f"{datos_usuario.get('dias_vacaciones_tomadas', 0)} dias"), 0, 1)
    
    pdf.set_x(110)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(45, 6, clean_txt('CTS ya pagada:'), 0, 0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 6, clean_txt(f"S/ {datos_usuario.get('cts_ya_pagada', 0.0):.2f}"), 0, 1)
    
    pdf.set_x(110)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(45, 6, clean_txt('Gratif. ya pagadas:'), 0, 0)
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(45, 6, clean_txt(f"S/ {datos_usuario.get('gratif_ya_pagada', 0.0):.2f}"), 0, 1)
    
    pdf.set_xy(10, pdf.get_y() + 15) # Ajustar posición Y después del rectángulo
    pdf.ln(5)
    
    # 2. Diagnóstico de Laboralidad
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, clean_txt('2. DIAGNOSTICO DE SOLIDEREZ DEL CASO'), 0, 1)
    
    puntaje = scorecard['puntaje']
    categoria = scorecard['categoria']
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(2, 132, 199) # Sky-600
    pdf.cell(50, 6, clean_txt('Indice de Solidez:'), 0, 0)
    pdf.cell(0, 6, clean_txt(f"{puntaje}/100 - {categoria}"), 0, 1)
    
    pdf.set_font('Helvetica', '', 9.5)
    pdf.set_text_color(51, 65, 85) # Slate-700
    pdf.multi_cell(0, 5, clean_txt(scorecard['explicacion']))
    pdf.ln(5)
    
    # 3. Liquidación de Beneficios (sólo si es DL 728)
    if datos_usuario['regimen'] == 'Privado (DL 728)' and liquidacion:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, clean_txt('3. DETALLE DE LIQUIDACION DE BENEFICIOS (DL 728)'), 0, 1)
        pdf.set_font('Helvetica', 'B', 9)
        
        # Tabla de Liquidación
        # Encabezado con estilo
        pdf.set_fill_color(15, 23, 42) # Slate-900 background
        pdf.set_text_color(255, 255, 255)
        pdf.cell(75, 8, clean_txt(' Concepto'), 1, 0, 'L', True)
        pdf.cell(57, 8, clean_txt('Monto Reclamable (Neto)'), 1, 0, 'R', True)
        pdf.cell(58, 8, clean_txt('Monto Prescrito (Perdido)'), 1, 1, 'R', True)
        
        pdf.set_text_color(51, 65, 85)
        pdf.set_font('Helvetica', '', 9)
        
        # Filas
        conceptos = [
            ('CTS (Compensacion de Tiempo de Servicios)', liquidacion.cts_reclamable, liquidacion.cts_prescrito),
            ('Gratificaciones (Julio y Diciembre)', liquidacion.gratif_reclamable, liquidacion.gratif_prescrito),
            ('Vacaciones Truncas / No Gozadas', liquidacion.vac_reclamable, liquidacion.vac_prescrito),
            ('Bonificacion Extraordinaria (Ley 29351 - 9%)', liquidacion.bonif_reclamable, liquidacion.bonif_prescrito),
            ('Interes Legal Laboral (Decreto Ley 25920)', liquidacion.interes_reclamable, liquidacion.interes_prescrito)
        ]
        
        for i, (name, rec, pres) in enumerate(conceptos):
            # Alternar color de fila
            if i % 2 == 0:
                pdf.set_fill_color(248, 250, 252)
            else:
                pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(75, 7, clean_txt(f" {name}"), 1, 0, 'L', True)
            pdf.cell(57, 7, f"S/ {rec:.2f}", 1, 0, 'R', True)
            pdf.cell(58, 7, f"S/ {pres:.2f}", 1, 1, 'R', True)
        
        # Totales
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_fill_color(224, 242, 254) # Sky-100 bg
        pdf.set_text_color(3, 105, 161) # Sky-700 text
        pdf.cell(75, 8, clean_txt(' TOTAL ESTIMADO A RECLAMAR'), 1, 0, 'L', True)
        pdf.cell(57, 8, f"S/ {liquidacion.total_reclamable:.2f}", 1, 0, 'R', True)
        pdf.cell(58, 8, f"S/ {liquidacion.total_prescrito:.2f}", 1, 1, 'R', True)
        pdf.ln(5)
        
        pdf.set_text_color(51, 65, 85) # Reset
        
        if liquidacion.prescrito_totalmente:
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(220, 38, 38) # Red-600
            pdf.multi_cell(0, 5, clean_txt("ALERTA DE PRESCRIPCION: Han transcurrido mas de 4 anos desde el cese laboral (Ley 27321). Toda accion de cobro podria ser declarada prescrita judicialmente."))
            pdf.set_text_color(51, 65, 85)
            pdf.ln(5)
    elif datos_usuario['regimen'] == 'Público (Ley 24041 / DL 276)':
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, clean_txt('3. ORIENTACION DE REGIMEN PUBLICO (Ley 24041)'), 0, 1)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 5, clean_txt("La desnaturalizacion en el Sector Publico no otorga beneficios del regimen 728 de forma directa. Otorga derecho a la reincorporacion laboral o estabilidad en la plaza correspondientes."))
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(194, 65, 12) # Orange-700
        pdf.multi_cell(0, 5, clean_txt("Precedente Huatuco (Cas. 5057-2013-Junin): Exige concurso publico de meritos en plaza vacante presupuestada de naturaleza permanente para la reincorporacion indefinida."))
        pdf.ln(5)
    else:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 8, clean_txt('3. ORIENTACION DE REGIMEN CAS (DL 1057)'), 0, 1)
        pdf.set_font('Helvetica', '', 9.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 5, clean_txt("El regimen CAS otorga estabilidad laboral relativa y la posibilidad de reposicion en caso de despido incausado o el pago de la indemnización por despido arbitrario segun jurisprudencia vinculante."))
        pdf.ln(5)
        
    # 4. Jurisprudencia de Soporte
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, clean_txt('4. JURISPRUDENCIA APLICABLE Y CASOS RELACIONADOS'), 0, 1)
    
    import re
    
    for i, sent in enumerate(sentencias):
        titulo_raw = sent['titulo']
        
        # Determinar el sentido del fallo
        fallo_amigable = "Fallo no especificado"
        if "Fundada" in titulo_raw:
            fallo_amigable = "GANO EL TRABAJADOR (Demanda Fundada)"
        elif "Infundada" in titulo_raw:
            fallo_amigable = "GANO EL EMPLEADOR (Demanda Infundada)"
        elif "Improcedente" in titulo_raw:
            fallo_amigable = "Improcedente"
            
        exp_match = re.search(r'(\d+-\d{4})', titulo_raw)
        expediente = f"Expediente N. {exp_match.group(1)}" if exp_match else titulo_raw
        
        # Limpiar abstract
        abstract_limpio = sent['abstract'].strip()
        abstract_limpio = re.sub(r'^\d+\.\s*(?:Que\s+)?', '', abstract_limpio)
        abstract_limpio = abstract_limpio[0].upper() + abstract_limpio[1:] if abstract_limpio else ""
        
        pdf.set_font('Helvetica', 'B', 9.5)
        pdf.set_text_color(15, 23, 42)
        url_sentencia = sent.get('url', '')
        pdf.cell(0, 6, clean_txt(f"Caso {i+1}: {expediente} (Similitud: {sent['similitud']*100:.1f}%)"), 0, 1, link=url_sentencia)
        
        # Enlace de descarga oficial
        if url_sentencia:
            pdf.set_font('Helvetica', 'B', 8.5)
            pdf.set_text_color(2, 132, 199) # Sky-600
            pdf.cell(0, 4, clean_txt("-> Ver Resolucion Completa en El Peruano (PDF Oficial)"), 0, 1, link=url_sentencia)
            pdf.set_text_color(51, 65, 85)
            
        # Sentido del fallo
        pdf.set_font('Helvetica', 'B', 8.5)
        if "GANO EL TRABAJADOR" in fallo_amigable:
            pdf.set_text_color(22, 163, 74) # Green-600
        else:
            pdf.set_text_color(100, 116, 139) # Slate-500
        pdf.cell(0, 5, clean_txt(f"Fallo del Tribunal: {fallo_amigable}"), 0, 1)
        pdf.set_text_color(51, 65, 85)
        
        # Abstract
        pdf.set_font('Helvetica', '', 8.5)
        pdf.multi_cell(0, 4, clean_txt(abstract_limpio[:340] + "..."))
        pdf.ln(3)
        
    # 5. Disclaimer Legal
    pdf.ln(4)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 3.5, clean_txt("DISCLAIMER: Esta es una herramienta de orientacion algoritmica y no constituye asesoria legal formal. Los calculos y analisis de solidez son referenciales y se basan en criterios jurisprudenciales generales. Para iniciar acciones legales o administrativas, se aconseja consultar con un abogado laboralista o acudir a SUNAFIL."))
    
    pdf.output(output_path)
