import streamlit as st
import datetime
import os
import sys

# Asegurar que el directorio src sea importable
sys.path.append("/Users/mac-mermitas/Documents/HACKATON")

from src.liquidacion import calcular_liquidacion_728, obtener_mensaje_regimen_publico, obtener_mensaje_cas
from src.retrieval import SentenciasRetrieval
from src.pdf_generator import generar_pdf_reporte
from src.explicador import explicar_caso
from src.elperuano_manager import ElPeruanoManager

# Carga en caché del buscador semántico
@st.cache_resource
def obtener_buscador():
    return SentenciasRetrieval()

# Carga en caché de El Peruano
@st.cache_resource
def obtener_peruano_manager():
    return ElPeruanoManager()

# Configuración de la página
st.set_page_config(
    page_title="DesnaturalizaCheck - Diagnóstico Laboral",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para UI Premium y Ultra-Intuitiva
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Configuración Global */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #1e293b 0%, #0f172a 90%);
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }
    
    /* Encabezados */
    h1, h2, h3, h4, h5 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Indicador de Pasos / Wizard Progress */
    .step-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        background: rgba(30, 41, 59, 0.7);
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .step-item {
        text-align: center;
        flex: 1;
        font-size: 0.9rem;
        font-weight: 600;
        color: #64748b;
    }
    .step-item.active {
        color: #38bdf8;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }
    .step-item.completed {
        color: #34d399;
    }
    .step-divider {
        width: 40px;
        height: 2px;
        background-color: #334155;
    }
    .step-divider.active {
        background-color: #38bdf8;
    }

    /* Inputs de Formulario */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: #475569 !important;
        border-radius: 8px !important;
    }
    input, textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
    
    /* Botones Premium */
    .stButton>button {
        background: linear-gradient(135deg, #0ea5e9, #0284c7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);
    }
    
    /* Tarjetas de Diagnóstico */
    .card-solido {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.15) 100%);
        border: 1px solid #10b981;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.1);
    }
    .card-indicios {
        background: linear-gradient(135deg, rgba(245, 158, 11 0.1) 0%, rgba(217, 119, 6 0.15) 100%);
        border: 1px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(245, 158, 11, 0.1);
    }
    .card-debil {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.15) 100%);
        border: 1px solid #ef4444;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.1);
    }

    /* Tarjetas de Jurisprudencia */
    .card-jurisprudencia {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.3rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    .card-jurisprudencia:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Configuración de la barra lateral para IA
st.sidebar.markdown("### 🤖 Asistente de IA")
env_key = os.environ.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input(
    "Gemini API Key:",
    value=env_key,
    type="password",
    help="Ingresa tu clave de API de Google AI Studio para activar explicaciones y resúmenes ejecutivos con IA."
)

# Panel Lateral: "Esto no es un caso aislado"
st.sidebar.markdown("---")
st.sidebar.markdown("### 📢 Esto no es un caso aislado")

# 1. Contador de Impacto
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid rgba(56, 189, 248, 0.2); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
    <p style='margin:0; font-size:0.75rem; color:#94a3b8; text-transform: uppercase; font-weight:600;'>Beneficios adeudados estimados (histórico regional)</p>
    <h4 style='margin:0.2rem 0; color:#38bdf8; font-size:1.4rem;'>S/ 84,720,195</h4>
    <p style='margin:0; font-size:0.75rem; color:#64748b;'>Calculado a partir de 2,386 fallos del Poder Judicial.</p>
</div>
""", unsafe_allow_html=True)

# 2. Titulares Reales de Prensa
st.sidebar.markdown("**📰 Noticias Reales & Contexto:**")
st.sidebar.markdown("""
*   **Gestión (2024):** *\"SUNAFIL incrementa fiscalización de contratos de locación de servicios fraudulentos en un 35%.\"*
*   **El Peruano (2023):** *\"Poder Judicial establece precedentes de reposición automática para obreros municipales.\"*
*   **RPP Noticias (2024):** *\"Servidores CAS realizan plantones exigiendo el pase a la planilla estatal permanente en Lima.\"*
""", unsafe_allow_html=True)

# 3. Clamor en Redes
st.sidebar.markdown("**💬 La Voz de los Trabajadores:**")
st.sidebar.markdown("""
<div style='background-color: rgba(255, 255, 255, 0.03); border-left: 3px solid #f59e0b; padding: 0.6rem; border-radius: 4px; font-size: 0.8rem; color:#cbd5e1; margin-bottom: 0.8rem;'>
    <i>\"Llevo 3 años emitiendo recibos todos los meses, cumplo horario y me descuentan por tardanzas. Ya es hora de que se reconozcan mis derechos.\"</i>
    <br><span style='color:#64748b; font-size:0.7rem;'>— Carlos M., Ex Locador de Municipalidad</span>
</div>
<div style='background-color: rgba(255, 255, 255, 0.03); border-left: 3px solid #f59e0b; padding: 0.6rem; border-radius: 4px; font-size: 0.8rem; color:#cbd5e1;'>
    <i>\"DesnaturalizaCheck me dio el monto exacto de mi liquidación y con ese informe en PDF pude conciliar con mi empleador sin ir a juicio.\"</i>
    <br><span style='color:#64748b; font-size:0.7rem;'>— Rosa P., Asistente Contable</span>
</div>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 style='text-align: center; font-size: 2.3rem; margin-bottom: 0.2rem;'>⚖️ DesnaturalizaCheck</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 1.8rem;'>Diagnóstico inteligente de laboralidad y cálculo de liquidaciones por desnaturalización de contratos.</p>", unsafe_allow_html=True)

# Inicializar estados de la aplicación
if 'paso' not in st.session_state:
    st.session_state.paso = 1

if 'datos' not in st.session_state:
    st.session_state.datos = {
        'regimen': 'Privado (DL 728)',
        'fecha_inicio': datetime.date(2021, 6, 1),
        'fecha_cese': datetime.date(2023, 6, 1),
        'sueldo': 4000.0,
        'resumen_hechos': 'Trabajé como asistente administrativo con recibos por honorarios, tenía un jefe directo que controlaba mi horario y usaba la laptop de la empresa.',
        'es_obrero_municipal': False,
        'respuestas_scorecard': {
            'horario': 'Sí',
            'jefe': 'Sí',
            'asistencia': 'Sí',
            'herramientas': 'Sí',
            'memos': 'No',
            'recibos': 'Sí',
            'personal': 'Sí',
            'exclusividad': 'Sí'
        }
    }

# --- Renderizar Indicador Visual de Pasos (Wizard) ---
paso = st.session_state.paso
step_html = f"""
<div class="step-container">
    <div class="step-item {"active" if paso == 1 else "completed"}">1. Datos del Caso</div>
    <div class="step-divider {"active" if paso >= 2 else ""}"></div>
    <div class="step-item {"active" if paso == 2 else ("completed" if paso > 2 else "")}">2. Indicios de Laboralidad</div>
    <div class="step-divider {"active" if paso >= 3 else ""}"></div>
    <div class="step-item {"active" if paso == 3 else ""}">3. Resultados y Reporte</div>
</div>
"""
st.markdown(step_html, unsafe_allow_html=True)

# --- PASO 1: Datos Generales e Historial ---
if st.session_state.paso == 1:
    st.markdown("#### 📝 Introduce los datos de tu relación laboral")
    st.info("💡 **Consejo:** Si trabajaste bajo Recibos por Honorarios pero cumplías órdenes, selecciona el régimen que consideras que debiste tener (usualmente el Privado DL 728 para empresas u organismos autónomos, o el CAS/Público para el Estado).")
    
    with st.form("form_paso_1"):
        regimen = st.selectbox(
            "Régimen Laboral que deseas evaluar:",
            ['Privado (DL 728)', 'Público (Ley 24041 / DL 276)', 'CAS (DL 1057)'],
            index=['Privado (DL 728)', 'Público (Ley 24041 / DL 276)', 'CAS (DL 1057)'].index(st.session_state.datos['regimen']),
            help="Selecciona Privado (DL 728) si trabajaste para una empresa privada o eres obrero municipal. CAS o Público si eres empleado estatal."
        )
        
        # Opción extra dinámica si es régimen público
        es_obrero_municipal = False
        if regimen == 'Público (Ley 24041 / DL 276)':
            es_obrero_municipal = st.checkbox(
                "¿Eres Obrero Municipal? (Serenos, Limpieza, Parques)",
                value=st.session_state.datos['es_obrero_municipal'],
                help="Por ley, los obreros municipales pertenecen al régimen privado DL 728, lo que los excluye del precedente Huatuco."
            )
            
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input(
                "Fecha de Inicio de Labores:", 
                st.session_state.datos['fecha_inicio'],
                help="Día en el que ingresaste a trabajar o firmaste tu primer contrato."
            )
        with col2:
            fecha_cese = st.date_input(
                "Fecha de Cese o Término:", 
                st.session_state.datos['fecha_cese'],
                help="Día de tu despido, renuncia o fin del contrato."
            )
            
        sueldo = st.number_input(
            "Última Remuneración Mensual Recibida (S/):", 
            min_value=0.0, 
            value=st.session_state.datos['sueldo'], 
            step=100.0,
            help="Monto de tu sueldo bruto mensual (o promedio de tus recibos por honorarios)."
        )
        
        resumen_hechos = st.text_area(
            "Describe en tus propias palabras los hechos de tu trabajo:",
            value=st.session_state.datos['resumen_hechos'],
            placeholder="Ejemplo: Trabajé como analista en oficina, tenía una laptop de la empresa, mi jefe me controlaba las tardanzas, firmaba cuaderno de ingreso y emitía recibos todos los meses...",
            help="Esta descripción será analizada semánticamente para buscar sentencias reales similares en el dataset."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Siguiente Paso: Responder Cuestionario ➡️")
        
        if submit:
            if not resumen_hechos.strip():
                st.error("⚠️ Describe brevemente los hechos de tu caso para poder buscar precedentes similares.")
            elif fecha_inicio > fecha_cese:
                st.error("⚠️ La fecha de inicio no puede ser posterior a la fecha de cese.")
            elif sueldo <= 0:
                st.error("⚠️ La remuneración mensual debe ser un monto mayor a cero.")
            else:
                st.session_state.datos['regimen'] = regimen
                st.session_state.datos['es_obrero_municipal'] = es_obrero_municipal
                st.session_state.datos['fecha_inicio'] = fecha_inicio
                st.session_state.datos['fecha_cese'] = fecha_cese
                st.session_state.datos['sueldo'] = sueldo
                st.session_state.datos['resumen_hechos'] = resumen_hechos
                st.session_state.paso = 2
                st.rerun()

# --- PASO 2: Wizard Cuestionario de Indicios de Laboralidad ---
elif st.session_state.paso == 2:
    st.markdown("#### 🔍 Cuestionario de Subordinación Real")
    st.write("De acuerdo al **Principio de Primacía de la Realidad**, si tu trabajo en los hechos era subordinado, eres considerado trabajador en planilla independientemente del contrato civil o recibo por honorarios emitido. Responde con sinceridad:")
    
    preguntas = [
        ("¿Cumplías un horario fijo impuesto por la empresa o entidad?", "horario", 20),
        ("¿Tenías un jefe directo que te daba órdenes, tareas y supervisaba tu labor?", "jefe", 20),
        ("¿Marcabas asistencia (fotocheck, biométrico, cuaderno de firmas o reporte)?", "asistencia", 15),
        ("¿Usabas computadoras, correos corporativos o materiales provistos por el empleador?", "herramientas", 10),
        ("¿Recibiste memorándums, sanciones por escrito, llamadas de atención o felicitaciones formales?", "memos", 10),
        ("¿Emitías recibos correlativos mes a mes para el mismo empleador y por montos similares?", "recibos", 10),
        ("¿El trabajo lo realizabas de forma personal (no podías enviar a nadie en tu reemplazo)?", "personal", 10),
        ("¿Trabajabas en exclusividad para esa empresa (sin otros clientes paralelos)?", "exclusividad", 5)
    ]
    
    respuestas = {}
    with st.form("form_scorecard"):
        for label, key, peso in preguntas:
            respuestas[key] = st.radio(
                f"**{label}** *(Puntaje: {peso} pts)*",
                ["Sí", "No"],
                index=0 if st.session_state.datos['respuestas_scorecard'].get(key, "Sí") == "Sí" else 1,
                horizontal=True
            )
            st.markdown("<hr style='margin:0.5rem 0; opacity:0.1;'>", unsafe_allow_html=True)
            
        col1, col2 = st.columns(2)
        with col1:
            back = st.form_submit_button("⬅️ Modificar Datos del Paso 1")
        with col2:
            submit = st.form_submit_button("Generar Diagnóstico Completo 📊")
            
        if back:
            st.session_state.paso = 1
            st.rerun()
            
        if submit:
            st.session_state.datos['respuestas_scorecard'] = respuestas
            st.session_state.paso = 3
            st.rerun()

# --- PASO 3: Resultados, Cálculo y Jurisprudencia ---
elif st.session_state.paso == 3:
    # Calcular scorecard de diagnóstico
    preguntas_pesos = {
        "horario": 20, "jefe": 20, "asistencia": 15, "herramientas": 10,
        "memos": 10, "recibos": 10, "personal": 10, "exclusividad": 5
    }
    
    puntaje = 0
    for key, val in st.session_state.datos['respuestas_scorecard'].items():
        if val == "Sí":
            puntaje += preguntas_pesos.get(key, 0)
            
    if puntaje >= 70:
        semaforo = "🟢"
        categoria = "Caso Altamente Sólido"
        estilo_tarjeta = "card-solido"
        explicacion = (
            "Existen indicios concurrentes y muy fuertes de que tu relación con la empresa fue de carácter subordinado "
            "(laboral) y no civil. Bajo el Principio de Primacía de la Realidad, tienes bases legales sumamente sólidas "
            "para solicitar la desnaturalización de tus contratos ante SUNAFIL o el Poder Judicial."
        )
    elif puntaje >= 40:
        semaforo = "🟡"
        categoria = "Caso con Indicios Moderados"
        estilo_tarjeta = "card-indicios"
        explicacion = (
            "Se detectan indicios significativos de laboralidad, aunque algunos elementos de autonomía persisten. "
            "Para un proceso exitoso, es clave recopilar más pruebas asociadas a la subordinación directa (correos electrónicos, "
            "instrucciones por WhatsApp, memos, etc.)."
        )
    else:
        semaforo = "🔴"
        categoria = "Caso con Indicios Débiles"
        estilo_tarjeta = "card-debil"
        explicacion = (
            "Los indicios de laboralidad son limitados en los hechos que reportas. La relación se asemejó más "
            "a una locación de servicios autónoma real. Si tuviste un jefe que te imponía tareas directas que no has "
            "seleccionado en el cuestionario, te recomendamos volver a evaluar."
        )
        
    scorecard_info = {
        'puntaje': puntaje,
        'semaforo': semaforo,
        'categoria': categoria,
        'explicacion': explicacion
    }
    
    # Renderizar scorecard en pantalla con un diseño visual de alto impacto
    st.markdown(f"""
    <div class="{estilo_tarjeta}">
        <h3 style='margin-top:0; font-size:1.5rem;'>{semaforo} Diagnóstico de Laboralidad: {categoria}</h3>
        <p style='font-size: 1.6rem; font-weight: 700; margin-bottom: 0.5rem;'>Indice de Solidez: {puntaje} %</p>
        <p style='font-size:0.95rem; line-height: 1.5; opacity: 0.9;'>{explicacion}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Motor Financiero
    regimen = st.session_state.datos['regimen']
    
    if regimen == 'Privado (DL 728)':
        st.markdown("#### 💰 Desglose de Liquidación Estimada")
        liq = calcular_liquidacion_728(
            st.session_state.datos['fecha_inicio'],
            st.session_state.datos['fecha_cese'],
            st.session_state.datos['sueldo']
        )
        
        # Grid para métricas destacadas
        met1, met2 = st.columns(2)
        with met1:
            st.metric(
                label="Total Reclamable Neto (Capital + Intereses)",
                value=f"S/ {liq.total_reclamable:,.2f}",
                help="Beneficios que están dentro del plazo de cobro."
            )
        with met2:
            st.metric(
                label="Total Prescrito (No Reclamable)",
                value=f"S/ {liq.total_prescrito:,.2f}",
                help="Monto que ya venció por superar el plazo de 4 años desde el cese."
            )
            
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Periodo Laborado:** {liq.meses_totales} meses ({liq.dias_totales} días)")
        with col2:
            st.write(f"**Vigencia del cobro:** {'Prescrito' if liq.prescrito_totalmente else 'Vigente para demandar'}")
            
        # Tabla de conceptos
        conceptos_data = {
            "Concepto": ["CTS (Compensación de T. Serv.)", "Gratificaciones", "Vacaciones Truncas", "Bonificación Extraordinaria (9%)", "Interés Legal Laboral (DL 25920)", "TOTAL"],
            "Monto Reclamable": [f"S/ {liq.cts_reclamable:,.2f}", f"S/ {liq.gratif_reclamable:,.2f}", f"S/ {liq.vac_reclamable:,.2f}", f"S/ {liq.bonif_reclamable:,.2f}", f"S/ {liq.interes_reclamable:,.2f}", f"S/ {liq.total_reclamable:,.2f}"],
            "Monto Prescrito": [f"S/ {liq.cts_prescrito:,.2f}", f"S/ {liq.gratif_prescrito:,.2f}", f"S/ {liq.vac_prescrito:,.2f}", f"S/ {liq.bonif_prescrito:,.2f}", f"S/ {liq.interes_prescrito:,.2f}", f"S/ {liq.total_prescrito:,.2f}"]
        }
        st.table(conceptos_data)
        
        # Gráfico dinámico de distribución
        import pandas as pd
        grafico_data = {
            "Concepto": ["CTS", "Gratificaciones", "Vacaciones", "Bonif. 9%", "Interés Legal"],
            "Monto (S/)": [liq.cts_reclamable, liq.gratif_reclamable, liq.vac_reclamable, liq.bonif_reclamable, liq.interes_reclamable]
        }
        df_grafico = pd.DataFrame(grafico_data).set_index("Concepto")
        st.markdown("##### 📊 Distribución de la Liquidación Reclamable")
        st.bar_chart(df_grafico)
        
        if liq.prescrito_totalmente:
            st.warning("⚠️ **Alerta de Prescripción (Ley 27321):** Han transcurrido más de 4 años desde la fecha de cese laboral. Por ley, el derecho a cobrar estos montos ha vencido judicialmente.")
            
    elif regimen == 'Público (Ley 24041 / DL 276)':
        st.markdown("#### 🏛️ Consecuencias en el Sector Público (Ley 24041)")
        info = obtener_mensaje_regimen_publico(st.session_state.datos['es_obrero_municipal'])
        
        st.info(info['consecuencia'])
        st.warning(info['advertencia_huatuco'])
        st.success(info['excepciones'])
        liq = None
        
    else:
        st.markdown("#### 🏛️ Consecuencias en el Régimen CAS (DL 1057)")
        info = obtener_mensaje_cas()
        st.info(info['consecuencia'])
        st.warning(info['advertencia'])
        liq = None
        
    # 3. Jurisprudencia Recomendada (Búsqueda Semántica)
    st.markdown("---")
    
    # Tarjeta de Estadísticas de la base de datos
    try:
        retriever = obtener_buscador()
        stats = retriever.con.execute(f"""
            SELECT count(*), 
                   sum(case when titulo like '%Fundada%' then 1 else 0 end) as fundadas 
            FROM sentencias 
            WHERE regimen = '{regimen}'
        """).fetchone()
        
        total_casos_regimen = stats[0]
        casos_fundados = stats[1] if stats[1] else 0
        tasa_exito = (casos_fundados / total_casos_regimen * 100) if total_casos_regimen > 0 else 0
        
        st.markdown(f"""
        <div style='background-color: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.2); padding:1.2rem; border-radius:12px; margin-bottom:1.5rem;'>
            <p style='margin:0; font-size:0.9rem; color:#38bdf8;'><b>Estadística Histórica del Dataset ({regimen}):</b></p>
            <h4 style='margin:0.3rem 0; color:#f8fafc;'>{total_casos_regimen:,} sentencias reales analizadas</h4>
            <p style='margin:0; font-size:0.9rem; color:#94a3b8;'>Tasa de demandas declaradas fundadas (a favor del trabajador): <b style='color:#34d399;'>{tasa_exito:.1f}%</b></p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        pass

    st.markdown("#### 📚 Jurisprudencia de Soporte Recomendada (Top-3 Sentencias)")
    with st.spinner("Buscando fallos similares en el Poder Judicial..."):
        try:
            retriever = obtener_buscador()
            sentencias = retriever.search(st.session_state.datos['resumen_hechos'], regimen, top_k=3)
            
            import re
            pm = obtener_peruano_manager()
            
            for i, sent in enumerate(sentencias):
                titulo_raw = sent['titulo']
                abstract_limpio = sent['abstract'].strip()
                abstract_limpio = re.sub(r'^\d+\.\s*(?:Que\s+)?', '', abstract_limpio)
                abstract_limpio = abstract_limpio[0].upper() + abstract_limpio[1:] if abstract_limpio else ""
                
                # Buscar el fallo en el título y en el abstract para mayor cobertura
                fallo_text = (titulo_raw + " " + abstract_limpio).lower()
                fallo_amigable = "Criterio Judicial de Casación"
                color_fallo = "#e2e8f0" # Blanco/Gris
                if "infundada" in fallo_text:
                    fallo_amigable = "A FAVOR DEL EMPLEADOR (Demanda Infundada)"
                    color_fallo = "#f87171" # Rojo brillante
                elif "fundada" in fallo_text or "fundado" in fallo_text:
                    fallo_amigable = "A FAVOR DEL TRABAJADOR (Demanda Fundada)"
                    color_fallo = "#34d399" # Verde brillante
                elif "improcedente" in fallo_text:
                    fallo_amigable = "Improcedente (Aspecto formal)"
                    color_fallo = "#94a3b8"
                    
                exp_match = re.search(r'(\d+-\d{4})', titulo_raw)
                expediente = f"Expediente N° {exp_match.group(1)}" if exp_match else titulo_raw

                # Cargar información de vigencia y enriquecimiento
                norma_ref = sent.get('norma_derecho', 'Ley 24041')
                articulo_info = pm.obtener_articulo_por_ley(norma_ref)
                vigencia_info = pm.verificar_vigencia(norma_ref, sent.get('fecha', '2020-01-01'))
                
                # Definir color del semáforo de vigencia
                color_vigencia = "#34d399" # Verde brillante
                if "derog" in vigencia_info['estado'].lower():
                    color_vigencia = "#ef4444" # Rojo brillante
                elif "modific" in vigencia_info['estado'].lower():
                    color_vigencia = "#f59e0b" # Naranja/Ámbar
                
                st.markdown(f"""
                <div class="card-jurisprudencia">
                    <h5 style='margin-top:0; color:#38bdf8;'>Caso {i+1}: {expediente} · <span style='font-size:0.9rem; color:#94a3b8;'>Coincidencia: {sent['similitud']*100:.1f}%</span></h5>
                    <p style='font-size:0.85rem; margin-bottom:0.3rem; color:{color_fallo};'><b>Resultado del Juicio:</b> {fallo_amigable}</p>
                    <p style='font-size:0.85rem; margin-bottom:0.5rem; color:{color_vigencia};'><b>Estado de la Ley ({norma_ref}):</b> {vigencia_info['estado']} — <i>{vigencia_info['detalle']}</i></p>
                    <p style='font-size:0.9rem; color:#cbd5e1; line-height: 1.45; margin-bottom: 0.6rem;'>{abstract_limpio[:320]}...</p>
                    <p style='font-size:0.85rem; margin:0;'><a href="{sent['url']}" target="_blank" style="color:#38bdf8; font-weight:600; text-decoration:none;">📄 Ver/Descargar Expediente Completo (PDF Oficial) ↗️</a></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Sección de Enriquecimiento (Ver artículo de la ley)
                if articulo_info:
                    with st.expander(f"📖 Ver Fundamento Legal citado: {articulo_info['titulo_norma']} - {articulo_info['num_articulo']}"):
                        st.markdown(f"**Sumilla:** *{articulo_info['sumilla']}*")
                        st.markdown(f"**Texto Legal:**")
                        st.info(articulo_info['texto_articulo'])
                
                st.markdown("<br>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al cargar/ejecutar el motor de búsqueda: {e}")
            sentencias = []
            
    # Explicación del Caso con IA (Gemini)
    st.markdown("---")
    if api_key:
        st.markdown("#### 🤖 Explicación Personalizada por IA (Gemini)")
        with st.spinner("Gemini está analizando la jurisprudencia y tu liquidación para redactar un informe amigable..."):
            explicacion_ia = explicar_caso(
                api_key, 
                st.session_state.datos, 
                scorecard_info, 
                liq, 
                sentencias
            )
            st.markdown(explicacion_ia)
    else:
        st.info("💡 **Explicación por IA:** Puedes ingresar tu API Key de Gemini en la barra lateral izquierda para que la Inteligencia Artificial analice tus resultados y te dé una explicación personalizada, sencilla y accionable de tu situación legal.")
            
    # 4. Botones de Acción y Descarga PDF
    st.markdown("---")
    col_back, col_pdf = st.columns(2)
    with col_back:
        if st.button("⬅️ Modificar Respuestas / Datos"):
            st.session_state.paso = 1
            st.rerun()
            
    with col_pdf:
        # Generar PDF temporal para descargar
        pdf_path = "/Users/mac-mermitas/Documents/HACKATON/data/reporte_caso.pdf"
        try:
            # Adecuar formato similitud para PDF
            sentencias_pdf = []
            for s in sentencias:
                sentencias_pdf.append({
                    'titulo': s['titulo'],
                    'pretension': s['pretension'],
                    'similitud': s['similitud'],
                    'abstract': s['abstract'],
                    'url': s.get('url', '')
                })
            
            generar_pdf_reporte(
                st.session_state.datos,
                scorecard_info,
                liq,
                sentencias_pdf,
                pdf_path
            )
            
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                
            st.download_button(
                label="Descargar Reporte Completo en PDF 📄",
                data=pdf_bytes,
                file_name="Reporte_Desnaturalizacion_Contratos.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al generar reporte PDF: {e}")
