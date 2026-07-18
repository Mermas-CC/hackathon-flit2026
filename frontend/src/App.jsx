import React, { useState } from 'react';

export default function App() {
  // Estados del Wizard
  const [paso, setPaso] = useState(1);
  const [apiKey, setApiKey] = useState("");
  
  // Datos del Caso (Valores predeterminados para debug "Next, Next")
  const [regimen, setRegimen] = useState("Privado (DL 728)");
  const [fechaInicio, setFechaInicio] = useState("2021-06-01");
  const [fechaCese, setFechaCese] = useState("2023-06-01");
  const [sueldo, setSueldo] = useState(4000.0);
  const [resumenHechos, setResumenHechos] = useState(
    "Trabajé como asistente administrativo con recibos por honorarios, tenía un jefe directo que controlaba mi horario y usaba la laptop de la empresa."
  );
  const [esObreroMunicipal, setEsObreroMunicipal] = useState(false);
  const [diasVacacionesTomadas, setDiasVacacionesTomadas] = useState(0);
  const [ctsYaPagada, setCtsYaPagada] = useState(0.0);
  const [gratifYaPagada, setGratifYaPagada] = useState(0.0);

  const [respuestasScorecard, setRespuestasScorecard] = useState({
    horario: "Sí",
    jefe: "Sí",
    asistencia: "Sí",
    herramientas: "Sí",
    memos: "No",
    recibos: "Sí",
    personal: "Sí",
    exclusividad: "Sí"
  });

  // Resultados de la API
  const [diagnostico, setDiagnostico] = useState(null);
  const [explicacionIa, setExplicacionIa] = useState(null);
  const [cargandoDiagnostico, setCargandoDiagnostico] = useState(false);
  const [cargandoIa, setCargandoIa] = useState(false);
  const [cargandoPdf, setCargandoPdf] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [cargandoBoleta, setCargandoBoleta] = useState(false);
  const [msgBoleta, setMsgBoleta] = useState("");
  const [precedenteSeleccionado, setPrecedenteSeleccionado] = useState(0);
  const [sidepanelAbierto, setSidepanelAbierto] = useState(false);

  // Preguntas del Scorecard
  const preguntas = [
    { label: "¿Cumplías un horario fijo impuesto por la empresa o entidad?", key: "horario", peso: 20 },
    { label: "¿Tenías un jefe directo que te daba órdenes, tareas y supervisaba tu labor?", key: "jefe", peso: 20 },
    { label: "¿Marcabas asistencia (fotocheck, biométrico, cuaderno de firmas o reporte)?", key: "asistencia", peso: 15 },
    { label: "¿Usabas computadoras, correos corporativos o materiales provistos por el empleador?", key: "herramientas", peso: 10 },
    { label: "¿Recibiste memorándums, sanciones por escrito, llamadas de atención o felicitaciones formales?", key: "memos", peso: 10 },
    { label: "¿Emitías recibos correlativos mes a mes para el mismo empleador y por montos similares?", key: "recibos", peso: 10 },
    { label: "¿El trabajo lo realizabas de forma personal (no podías enviar a nadie en tu reemplazo)?", key: "personal", peso: 10 },
    { label: "¿Trabajabas en exclusividad para esa empresa (sin otros clientes paralelos)?", key: "exclusividad", peso: 5 }
  ];

  const handleScorecardChange = (key, value) => {
    setRespuestasScorecard(prev => ({ ...prev, [key]: value }));
  };

  const renderTextoResaltado = (texto) => {
    if (!texto) return "";
    
    // Regex matching important indicators
    const regex = /(subordinación|relación de dependencia|bajo la dirección|instrucciones|órdenes|jefe inmediato|jefe de área|supervisión|horario de trabajo|marcar asistencia|registro de asistencia|control de asistencia|jornada laboral|horario fijo|recibos por honorarios|locación de servicios|pago mensual|contraprestación|sueldo|boletas de pago|sueldo mensual|exclusividad|exclusivo|permanencia|tiempo completo|duración ininterrumpida|continuidad|desnaturalización|desnaturalizado|primacía de la realidad|contrato de trabajo indeterminado)/gi;
    
    const partes = texto.split(regex);
    return partes.map((parte, index) => {
      const parteLower = parte.toLowerCase();
      
      let label = "";
      let classes = "";
      
      if (/(subordinación|relación de dependencia|bajo la dirección|instrucciones|órdenes|jefe inmediato|jefe de área|supervisión)/.test(parteLower)) {
        label = "Indicio: Subordinación Directa";
        classes = "bg-purple-500/25 text-purple-200 border-b-2 border-purple-500 px-0.5 rounded-t cursor-help relative group";
      } else if (/(horario de trabajo|marcar asistencia|registro de asistencia|control de asistencia|jornada laboral|horario fijo)/.test(parteLower)) {
        label = "Indicio: Horario y Jornada Controlada";
        classes = "bg-amber-500/25 text-amber-200 border-b-2 border-amber-500 px-0.5 rounded-t cursor-help relative group";
      } else if (/(recibos por honorarios|locación de servicios|pago mensual|contraprestación|sueldo|boletas de pago|sueldo mensual)/.test(parteLower)) {
        label = "Indicio: Pago Recurrente (Simulación)";
        classes = "bg-emerald-500/25 text-emerald-200 border-b-2 border-emerald-500 px-0.5 rounded-t cursor-help relative group";
      } else if (/(exclusividad|exclusivo|permanencia|tiempo completo|duración ininterrumpida|continuidad)/.test(parteLower)) {
        label = "Indicio: Exclusividad y Continuidad";
        classes = "bg-sky-500/25 text-sky-200 border-b-2 border-sky-500 px-0.5 rounded-t cursor-help relative group";
      } else if (/(desnaturalización|desnaturalizado|primacía de la realidad|contrato de trabajo indeterminado)/.test(parteLower)) {
        label = "Principio de Primacía de la Realidad";
        classes = "bg-rose-500/25 text-rose-200 border-b-2 border-rose-500 px-0.5 rounded-t cursor-help relative group";
      }
      
      if (label) {
        return (
          <span key={index} className={classes}>
            {parte}
            <span className="invisible group-hover:visible absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2.5 py-1 text-[10px] font-sans font-semibold bg-slate-950 text-slate-100 rounded border border-slate-700 shadow-xl whitespace-nowrap z-50">
              {label}
            </span>
          </span>
        );
      }
      
      return parte;
    });
  };

  const analizarBoletaImagen = async (file) => {
    setCargandoBoleta(true);
    setMsgBoleta("");
    setErrorMsg("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("api_key", apiKey);

      const response = await fetch("/api/analizar-boleta", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al procesar la boleta");
      }

      const data = await response.json();
      
      // Auto-completar los datos si vienen de la IA
      if (data.sueldo) setSueldo(parseFloat(data.sueldo));
      if (data.fecha_inicio) setFechaInicio(data.fecha_inicio);
      if (data.fecha_cese) setFechaCese(data.fecha_cese);
      if (data.dias_vacaciones_tomadas !== undefined) setDiasVacacionesTomadas(data.dias_vacaciones_tomadas);
      if (data.cts_ya_pagada !== undefined) setCtsYaPagada(data.cts_ya_pagada);
      if (data.gratif_ya_pagada !== undefined) setGratifYaPagada(data.gratif_ya_pagada);

      setMsgBoleta("✅ ¡Boleta analizada con éxito! Los campos se han autocompletado en el formulario.");
    } catch (e) {
      setErrorMsg(`Error al procesar boleta: ${e.message}`);
    } finally {
      setCargandoBoleta(false);
    }
  };

  // Intérprete simple de Markdown para mostrar el reporte de Gemini de forma limpia
  const renderizarMarkdown = (texto) => {
    if (!texto) return { __html: "" };
    
    // Escapar HTML para evitar XSS
    let html = texto
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
      
    // Títulos ###
    html = html.replace(/^### (.*$)/gim, '<h5 class="text-xs md:text-sm font-bold text-sky-400 mt-4 mb-2">$1</h5>');
    // Títulos ##
    html = html.replace(/^## (.*$)/gim, '<h4 class="text-sm md:text-base font-bold text-sky-300 mt-5 mb-2 border-b border-slate-800 pb-1">$1</h4>');
    // Títulos #
    html = html.replace(/^# (.*$)/gim, '<h3 class="text-base md:text-lg font-bold text-white mt-6 mb-3">$1</h3>');
    // Negritas **texto**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="text-sky-300 font-semibold">$1</strong>');
    // Viñetas * item o - item
    html = html.replace(/^\s*[\*\-]\s+(.*$)/gim, '<li class="ml-4 list-disc text-slate-300 my-1">$1</li>');
    // Citas > texto
    html = html.replace(/^\>\s+(.*$)/gim, '<blockquote class="border-l-4 border-purple-500 pl-3 italic text-slate-400 my-3">$1</blockquote>');
    // Saltos de línea
    html = html.replace(/\n/g, '<br />');

    return { __html: html };
  };

  // 1. Llamar al Diagnóstico
  const ejecutarDiagnostico = async () => {
    setCargandoDiagnostico(true);
    setErrorMsg("");
    try {
      const response = await fetch("/api/diagnostico", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          regimen,
          fecha_inicio: fechaInicio,
          fecha_cese: fechaCese,
          sueldo: parseFloat(sueldo),
          resumen_hechos: resumenHechos,
          es_obrero_municipal: esObreroMunicipal,
          respuestas_scorecard: respuestasScorecard,
          dias_vacaciones_tomadas: parseInt(diasVacacionesTomadas) || 0,
          cts_ya_pagada: parseFloat(ctsYaPagada) || 0.0,
          gratif_ya_pagada: parseFloat(gratifYaPagada) || 0.0
        })
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error en el servidor");
      }
      const data = await response.json();
      setDiagnostico(data);
      setPaso(3);
      
      // Auto-generar explicación con IA de forma asíncrona si hay API Key
      if (apiKey) {
        solicitarExplicacionIa(data);
      }
    } catch (e) {
      setErrorMsg(e.message);
    } finally {
      setCargandoDiagnostico(false);
    }
  };

  // 2. Llamar a la explicación de IA (Gemini)
  const solicitarExplicacionIa = async (diagData) => {
    setCargandoIa(true);
    try {
      const response = await fetch("/api/explicar-ia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          api_key: apiKey,
          datos_usuario: {
            regimen,
            fecha_inicio: fechaInicio,
            fecha_cese: fechaCese,
            sueldo: parseFloat(sueldo),
            resumen_hechos: resumenHechos,
            dias_vacaciones_tomadas: parseInt(diasVacacionesTomadas) || 0,
            cts_ya_pagada: parseFloat(ctsYaPagada) || 0.0,
            gratif_ya_pagada: parseFloat(gratifYaPagada) || 0.0
          },
          scorecard_info: diagData.scorecard,
          liquidacion: diagData.liquidacion,
          sentencias: diagData.sentencias
        })
      });
      const data = await response.json();
      setExplicacionIa(data.explicacion);
    } catch (e) {
      setExplicacionIa({
        error: true,
        resumen: "Error al generar análisis con IA",
        significado: "No se pudo establecer conexión con el servicio de análisis de Inteligencia Artificial.",
        analisis_detalle: e.message,
        pasos_sugeridos: [
          "Verifica que el servidor backend esté corriendo.",
          "Comprueba tu conexión de red.",
          "Intenta presionar 'Calcular Diagnóstico' nuevamente."
        ]
      });
    } finally {
      setCargandoIa(false);
    }
  };

  // 3. Descargar Reporte PDF
  const descargarPdf = async () => {
    setCargandoPdf(true);
    try {
      const response = await fetch("/api/reporte-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          datos_usuario: {
            regimen,
            fecha_inicio: fechaInicio,
            fecha_cese: fechaCese,
            sueldo: parseFloat(sueldo),
            resumen_hechos: resumenHechos,
            es_obrero_municipal: esObreroMunicipal,
            dias_vacaciones_tomadas: parseInt(diasVacacionesTomadas) || 0,
            cts_ya_pagada: parseFloat(ctsYaPagada) || 0.0,
            gratif_ya_pagada: parseFloat(gratifYaPagada) || 0.0
          },
          scorecard_info: diagnostico.scorecard,
          liquidacion: diagnostico.liquidacion,
          sentencias: diagnostico.sentencias
        })
      });
      if (!response.ok) throw new Error("Error al generar PDF");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "Reporte_Desnaturalizacion.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert(`Error al descargar el reporte: ${e.message}`);
    } finally {
      setCargandoPdf(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row text-slate-100">
      
      {/* --- PANEL LATERAL IZQUIERDO --- */}
      <aside className="w-full md:w-80 glass-panel p-6 flex flex-col border-b md:border-b-0 md:border-r border-slate-700/50">
        <div className="mb-8">
          <h2 className="text-2xl font-bold flex items-center gap-2 text-sky-400">
            MiLiqui
          </h2>
          <p className="text-xs text-slate-400 mt-1">Diagnóstico inteligente v2.0</p>
        </div>

        {/* Ingresar API Key */}
        <div className="mb-6">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
            🤖 Gemini API Key
          </label>
          <input
            type="password"
            className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Introduce tu API Key..."
          />
          <p className="text-[10px] text-slate-400 mt-1">
            Requerido para generar la explicación y sumillas inteligentes con IA.
          </p>
        </div>

        <hr className="border-slate-800 my-4" />

        {/* Estadística del panel */}
        <div className="mb-6 bg-slate-950/60 border border-sky-500/20 p-4 rounded-xl">
          <p className="text-[10px] uppercase font-bold text-sky-400 tracking-wider">
            Deuda Estimada Regional
          </p>
          <h3 className="text-2xl font-extrabold text-sky-300 mt-1">S/ 84,720,195</h3>
          <p className="text-[10px] text-slate-400 mt-1">
            Calculado sobre 2,386 sentencias reales del Poder Judicial.
          </p>
        </div>

        {/* Titulares de Prensa */}
        <div className="mb-6">
          <h4 className="text-xs font-bold text-slate-300 uppercase mb-2">📰 En las Noticias:</h4>
          <ul className="text-xs text-slate-400 space-y-2">
            <li className="border-l-2 border-slate-700 pl-2">
              <strong>SUNAFIL:</strong> Inspecciones de locaciones fraudulentas se disparan 35% en 2024.
            </li>
            <li className="border-l-2 border-slate-700 pl-2">
              <strong>El Peruano:</strong> PJ emite precedente a favor de reposición de obreros municipales.
            </li>
          </ul>
        </div>

        {/* Testimonios */}
        <div className="mt-auto">
          <h4 className="text-xs font-bold text-slate-300 uppercase mb-2">💬 La Voz del Locador:</h4>
          <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800 text-[11px] text-slate-300 italic">
            "Tenía un jefe, marcaba horario y emitía recibos todos los meses. Con este reporte obtuve las bases para mi demanda laboral."
            <span className="block text-[9px] text-slate-500 mt-1 not-italic font-bold">— Carlos M., Ex Locador</span>
          </div>
        </div>
      </aside>

      {/* --- PANEL PRINCIPAL --- */}
      <main className="flex-1 p-6 md:p-12 max-w-4xl mx-auto w-full">
        
        {/* Wizard Steps Progress Indicator */}
        <div className="flex justify-between items-center bg-slate-900/50 border border-slate-800 px-6 py-3 rounded-xl mb-8">
          <div className={`text-xs md:text-sm font-bold ${paso === 1 ? 'text-sky-400' : 'text-emerald-400'}`}>
            1. Datos del Caso
          </div>
          <div className={`h-[1px] w-12 bg-slate-800 ${paso >= 2 ? 'bg-sky-500' : ''}`} />
          <div className={`text-xs md:text-sm font-bold ${paso === 2 ? 'text-sky-400' : (paso > 2 ? 'text-emerald-400' : 'text-slate-500')}`}>
            2. Indicios de Subordinación
          </div>
          <div className={`h-[1px] w-12 bg-slate-800 ${paso >= 3 ? 'bg-sky-500' : ''}`} />
          <div className={`text-xs md:text-sm font-bold ${paso === 3 ? 'text-sky-400' : 'text-slate-500'}`}>
            3. Diagnóstico y Reporte
          </div>
        </div>

        {errorMsg && (
          <div className="bg-rose-950/50 border border-rose-500 text-rose-200 px-4 py-3 rounded-lg mb-6 text-sm">
            ⚠️ {errorMsg}
          </div>
        )}

        {/* --- PASO 1: Ingreso de Datos --- */}
        {paso === 1 && (
          <section className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-1">📝 Datos Generales de tu Relación Laboral</h3>
              <p className="text-sm text-slate-400">Introduce los periodos, sueldo y describe cómo trabajabas.</p>
            </div>

            <div className="glass-panel p-6 rounded-2xl space-y-4">
              
              {/* Uploader de Boleta con IA */}
              <div className="bg-slate-900/60 p-4 rounded-xl border border-dashed border-slate-700 hover:border-sky-500/50 transition-colors">
                <label className="block text-xs font-bold text-sky-400 uppercase tracking-wider mb-2">
                  📸 Auto-completado Multimodal por IA (Gemini 2.5)
                </label>
                <p className="text-[11px] text-slate-400 mb-3">
                  Sube una foto o captura de tu boleta de pago o liquidación. La IA extraerá los datos automáticamente.
                </p>
                <div className="flex flex-col sm:flex-row items-center gap-3">
                  <input
                    type="file"
                    accept="image/*"
                    className="block w-full text-xs text-slate-400
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-full file:border-0
                      file:text-xs file:font-semibold
                      file:bg-slate-800 file:text-sky-400
                      hover:file:bg-slate-700 file:cursor-pointer"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        analizarBoletaImagen(e.target.files[0]);
                      }
                    }}
                  />
                  {cargandoBoleta && (
                    <span className="text-xs text-sky-400 animate-pulse flex items-center gap-1">
                      <span>●</span> Procesando boleta...
                    </span>
                  )}
                </div>
                {msgBoleta && (
                  <p className="text-[11px] text-emerald-400 mt-2 font-medium">
                    {msgBoleta}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Régimen Laboral que consideras te corresponde:
                </label>
                <select
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
                  value={regimen}
                  onChange={(e) => setRegimen(e.target.value)}
                >
                  <option>Privado (DL 728)</option>
                  <option>Público (Ley 24041 / DL 276)</option>
                  <option>CAS (DL 1057)</option>
                </select>
              </div>

              {regimen === 'Público (Ley 24041 / DL 276)' && (
                <div className="flex items-center gap-2 p-3 bg-slate-900/60 border border-slate-800 rounded-lg">
                  <input
                    type="checkbox"
                    id="obrero"
                    checked={esObreroMunicipal}
                    onChange={(e) => setEsObreroMunicipal(e.target.checked)}
                    className="w-4 h-4 text-sky-500 border-slate-700 bg-slate-900 rounded focus:ring-sky-500"
                  />
                  <label htmlFor="obrero" className="text-sm text-slate-300">
                    ¿Eres Obrero Municipal? (Serenos, Limpieza, Parques y Jardines)
                  </label>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Fecha de Inicio de Labores:</label>
                  <input
                    type="date"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200"
                    value={fechaInicio}
                    onChange={(e) => setFechaInicio(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Fecha de Cese o Término:</label>
                  <input
                    type="date"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200"
                    value={fechaCese}
                    onChange={(e) => setFechaCese(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Sueldo Bruto Mensual (S/):</label>
                <input
                  type="number"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200"
                  value={sueldo}
                  onChange={(e) => setSueldo(parseFloat(e.target.value))}
                />
              </div>

              {regimen === 'Privado (DL 728)' && (
                <div className="bg-slate-950/40 p-4 rounded-xl border border-slate-800 space-y-3">
                  <h4 className="text-xs font-bold text-sky-400 uppercase tracking-wider">🛠️ Personalizar Beneficios Recibidos (Deducciones)</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-[11px] text-slate-400 mb-1">Días de vacaciones gozadas:</label>
                      <input
                        type="number"
                        className="w-full bg-slate-900 border border-slate-750 rounded-lg px-3 py-1.5 text-xs text-slate-200"
                        value={diasVacacionesTomadas}
                        onChange={(e) => setDiasVacacionesTomadas(parseInt(e.target.value) || 0)}
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] text-slate-400 mb-1">CTS ya pagada (S/):</label>
                      <input
                        type="number"
                        className="w-full bg-slate-900 border border-slate-750 rounded-lg px-3 py-1.5 text-xs text-slate-200"
                        value={ctsYaPagada}
                        onChange={(e) => setCtsYaPagada(parseFloat(e.target.value) || 0.0)}
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] text-slate-400 mb-1">Gratif. ya pagadas (S/):</label>
                      <input
                        type="number"
                        className="w-full bg-slate-900 border border-slate-750 rounded-lg px-3 py-1.5 text-xs text-slate-200"
                        value={gratifYaPagada}
                        onChange={(e) => setGratifYaPagada(parseFloat(e.target.value) || 0.0)}
                      />
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-500">
                    * Si ya recibiste pagos parciales de CTS, gratificaciones o gozaste vacaciones, regístralos para deducirlos del cálculo.
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Describe los Hechos de tu Trabajo:</label>
                <textarea
                  rows={4}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
                  placeholder="Ej. Emitía recibos por honorarios, marcaba tarjeta al entrar, me daban órdenes diarias, usaba laptop de la empresa..."
                  value={resumenHechos}
                  onChange={(e) => setResumenHechos(e.target.value)}
                />
              </div>
            </div>

            <button
              onClick={() => {
                if (!resumenHechos.trim()) {
                  setErrorMsg("⚠️ Describe brevemente los hechos de tu caso para buscar jurisprudencia similar.");
                } else {
                  setErrorMsg("");
                  setPaso(2);
                }
              }}
              className="w-full bg-gradient-to-r from-sky-500 to-sky-600 hover:from-sky-400 hover:to-sky-500 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:shadow-sky-500/20 transform hover:-translate-y-[1px] transition-all"
            >
              Siguiente Paso: Cuestionario de Indicios ➡️
            </button>
          </section>
        )}

        {/* --- PASO 2: Cuestionario de Indicios --- */}
        {paso === 2 && (
          <section className="space-y-6">
            <div>
              <h3 className="text-xl font-bold mb-1">🔍 Cuestionario de Subordinación Laboral</h3>
              <p className="text-sm text-slate-400">
                Responde Sí o No a estos criterios de primacía de la realidad judicial.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {preguntas.map((p) => {
                const esSi = respuestasScorecard[p.key] === "Sí";
                return (
                  <button
                    key={p.key}
                    onClick={() => handleScorecardChange(p.key, esSi ? "No" : "Sí")}
                    className={`p-4 rounded-xl text-left border transition-all flex flex-col justify-between h-32 ${
                      esSi 
                        ? "bg-emerald-950/20 border-emerald-500/50 hover:bg-emerald-950/30" 
                        : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-850"
                    }`}
                  >
                    <div className="flex justify-between items-center w-full">
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                        Criterio de Subordinación
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        esSi ? "bg-emerald-950 text-emerald-400 border border-emerald-500/30" : "bg-slate-950 text-slate-500 border border-slate-800"
                      }`}>
                        {esSi ? "SÍ" : "NO"}
                      </span>
                    </div>
                    <span className="text-xs md:text-sm font-medium text-slate-200 line-clamp-2 leading-relaxed">
                      {p.label}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${esSi ? "bg-emerald-400 animate-pulse" : "bg-slate-600"}`} />
                      <span className={`text-[10px] font-semibold ${esSi ? "text-emerald-400" : "text-slate-500"}`}>
                        {esSi ? "Indicio de laboralidad marcado" : "No aplica"}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setPaso(1)}
                className="bg-slate-800 hover:bg-slate-750 text-slate-300 font-bold py-3 px-6 rounded-lg border border-slate-700"
              >
                ⬅️ Atrás
              </button>
              <button
                onClick={ejecutarDiagnostico}
                disabled={cargandoDiagnostico}
                className="bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:shadow-emerald-500/20 disabled:opacity-50"
              >
                {cargandoDiagnostico ? "Generando Análisis..." : "Generar Diagnóstico Completo 📊"}
              </button>
            </div>
          </section>
        )}

        {/* --- PASO 3: Resultados --- */}
        {paso === 3 && diagnostico && (
          <section className="space-y-8">
            
            {/* Scorecard Solidez */}
            <div className={`p-6 rounded-2xl border ${
              diagnostico.scorecard.puntaje >= 70 
                ? 'bg-emerald-950/20 border-emerald-500/50 text-emerald-200' 
                : (diagnostico.scorecard.puntaje >= 40 ? 'bg-amber-950/20 border-amber-500/50 text-amber-200' : 'bg-rose-950/20 border-rose-500/50 text-rose-200')
            }`}>
              <h3 className="text-xl font-bold mb-2">
                {diagnostico.scorecard.semaforo} Diagnóstico de Laboralidad: {diagnostico.scorecard.categoria}
              </h3>
              <p className="text-3xl font-extrabold mb-2">
                Índice de Solidez: {diagnostico.scorecard.puntaje}%
              </p>
              <p className="text-sm opacity-90 leading-relaxed">
                {diagnostico.scorecard.explicacion}
              </p>
            </div>

            {/* Liquidación Monetaria */}
            {diagnostico.liquidacion ? (
              <div className="space-y-6">
                <h4 className="text-lg font-bold border-b border-slate-800 pb-2">💰 Liquidación Estimada</h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                    <p className="text-xs text-slate-400">Total Reclamable Neto (Capital + Intereses)</p>
                    <h3 className="text-2xl font-bold text-sky-400 mt-1">
                      S/ {diagnostico.liquidacion.total_reclamable.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </h3>
                  </div>
                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                    <p className="text-xs text-slate-400">Monto Prescrito (No Reclamable, plazo vencido)</p>
                    <h3 className="text-2xl font-bold text-slate-500 mt-1">
                      S/ {diagnostico.liquidacion.total_prescrito.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </h3>
                  </div>
                </div>

                {/* Conceptos en Tabla */}
                <div className="glass-panel rounded-xl overflow-hidden">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="bg-slate-950/40 text-slate-300">
                        <th className="p-3">Concepto</th>
                        <th className="p-3 text-right">Reclamable (S/)</th>
                        <th className="p-3 text-right text-slate-500">Prescrito (S/)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {[
                        { name: "CTS", rec: diagnostico.liquidacion.cts_reclamable, pres: diagnostico.liquidacion.cts_prescrito },
                        { name: "Gratificaciones", rec: diagnostico.liquidacion.gratif_reclamable, pres: diagnostico.liquidacion.gratif_prescrito },
                        { name: "Vacaciones Truncas", rec: diagnostico.liquidacion.vac_reclamable, pres: diagnostico.liquidacion.vac_prescrito },
                        { name: "Bonificación (9%)", rec: diagnostico.liquidacion.bonif_reclamable, pres: diagnostico.liquidacion.bonif_prescrito },
                        { name: "Interés Legal (DL 25920)", rec: diagnostico.liquidacion.interes_reclamable, pres: diagnostico.liquidacion.interes_prescrito },
                      ].map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-900/30">
                          <td className="p-3 font-medium">{item.name}</td>
                          <td className="p-3 text-right text-sky-300 font-semibold">S/ {item.rec.toFixed(2)}</td>
                          <td className="p-3 text-right text-slate-500">S/ {item.pres.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Gráfico de Barras Simple en HTML/CSS */}
                <div className="bg-slate-900/40 border border-slate-800 p-6 rounded-xl">
                  <h5 className="text-sm font-semibold mb-4 text-slate-300">📊 Distribución del Capital Reclamable</h5>
                  <div className="space-y-4">
                    {[
                      { label: "CTS", val: diagnostico.liquidacion.cts_reclamable, max: diagnostico.liquidacion.total_reclamable },
                      { label: "Gratificaciones", val: diagnostico.liquidacion.gratif_reclamable, max: diagnostico.liquidacion.total_reclamable },
                      { label: "Vacaciones Truncas", val: diagnostico.liquidacion.vac_reclamable, max: diagnostico.liquidacion.total_reclamable },
                      { label: "Bonificación 9%", val: diagnostico.liquidacion.bonif_reclamable, max: diagnostico.liquidacion.total_reclamable },
                      { label: "Interés Legal", val: diagnostico.liquidacion.interes_reclamable, max: diagnostico.liquidacion.total_reclamable },
                    ].map((bar, i) => {
                      const pct = bar.max > 0 ? (bar.val / bar.max) * 100 : 0;
                      return (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between text-xs font-medium">
                            <span className="text-slate-400">{bar.label}</span>
                            <span className="text-sky-300">S/ {bar.val.toFixed(2)} ({pct.toFixed(1)}%)</span>
                          </div>
                          <div className="w-full bg-slate-950 rounded-full h-3">
                            <div 
                              className="bg-sky-500 h-3 rounded-full" 
                              style={{ width: `${pct}%` }} 
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {diagnostico.liquidacion.prescrito_totalmente && (
                  <div className="bg-amber-950/20 border border-amber-500/50 p-4 rounded-xl text-xs text-amber-200">
                    ⚠️ <strong>Alerta de Prescripción (Ley 27321):</strong> Han transcurrido más de 4 años desde el cese laboral. Legalmente, el derecho de cobro judicial de estos conceptos ha prescrito.
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <h4 className="text-lg font-bold border-b border-slate-800 pb-2">🏛️ Consecuencias en el Sector Público</h4>
                <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
                  <p className="text-sm text-sky-300"><strong>Efecto Principal:</strong> {diagnostico.info_publico?.consecuencia}</p>
                  <p className="text-xs text-amber-200"><strong>Advertencia (Precedente Huatuco):</strong> {diagnostico.info_publico?.advertencia || diagnostico.info_publico?.advertencia_huatuco}</p>
                  {diagnostico.info_publico?.excepciones && (
                    <p className="text-xs text-emerald-300"><strong>Excepciones aplicables:</strong> {diagnostico.info_publico?.excepciones}</p>
                  )}
                </div>
              </div>
            )}

            {/* Jurisprudencia Enriquecida */}
            <div className="space-y-4">
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <h4 className="text-lg font-bold">📚 Precedentes Similares Citados</h4>
                {diagnostico.stats && (
                  <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/50 px-3 py-1 rounded-full border border-emerald-500/20">
                    Tasa de éxito del régimen: {diagnostico.stats.tasa_exito}% de fallos a favor ({diagnostico.stats.total_casos} casos)
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {diagnostico.sentencias.map((sent, index) => {
                  // Colores del fallo
                  let colorFallo = "text-slate-400 border-slate-800 bg-slate-950/40";
                  let falloLabel = "Criterio";
                  
                  const textLower = (sent.titulo + " " + sent.abstract).toLowerCase();
                  if (textLower.includes("infundada")) {
                    colorFallo = "text-rose-400 border-rose-500/20 bg-rose-950/20";
                    falloLabel = "Infundada";
                  } else if (textLower.includes("fundada") || textLower.includes("fundado")) {
                    colorFallo = "text-emerald-400 border-emerald-500/20 bg-emerald-950/20";
                    falloLabel = "Fundada";
                  } else if (textLower.includes("improcedente")) {
                    colorFallo = "text-slate-400 border-slate-700/20 bg-slate-850/20";
                    falloLabel = "Improcedente";
                  }
                  
                  // Color del semáforo de vigencia de El Peruano
                  let colorVigencia = "text-emerald-400 bg-emerald-950/40 border-emerald-500/20";
                  if (sent.vigencia_info?.estado?.includes("Derog")) {
                    colorVigencia = "text-rose-400 bg-rose-950/40 border-rose-500/20";
                  } else if (sent.vigencia_info?.estado?.includes("Modific")) {
                    colorVigencia = "text-amber-400 bg-amber-950/40 border-amber-500/20";
                  }

                  const similitudPct = sent.similitud * 100;
                  let colorSimilitudBar = "bg-sky-500";
                  if (similitudPct >= 80) colorSimilitudBar = "bg-emerald-500";
                  else if (similitudPct >= 60) colorSimilitudBar = "bg-amber-500";

                  return (
                    <div 
                      key={index} 
                      className="glass-panel p-5 rounded-xl flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all duration-300 shadow-md group relative hover:-translate-y-0.5"
                    >
                      <div className="space-y-3">
                        <div className="flex justify-between items-start gap-2">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                            Caso {index + 1}
                          </span>
                          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider ${colorFallo}`}>
                            {falloLabel}
                          </span>
                        </div>

                        <h5 className="font-bold text-slate-100 text-sm line-clamp-2 min-h-[2.5rem] group-hover:text-sky-400 transition-colors duration-200" title={sent.titulo}>
                          {sent.titulo}
                        </h5>

                        {/* Coincidencia visual */}
                        <div className="space-y-1">
                          <div className="flex justify-between items-center text-[10px]">
                            <span className="text-slate-500">Coincidencia factual</span>
                            <span className="text-slate-300 font-semibold">{similitudPct.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                            <div 
                              className={`h-full rounded-full transition-all duration-500 ${colorSimilitudBar}`}
                              style={{ width: `${similitudPct}%` }}
                            />
                          </div>
                        </div>

                        {/* Estado El Peruano */}
                        <div className="flex items-center gap-1.5 text-[10px] bg-slate-950/30 p-2 rounded border border-slate-900">
                          <span className={`w-2 h-2 rounded-full ${
                            sent.vigencia_info?.estado?.includes("Derog") ? "bg-red-500" : sent.vigencia_info?.estado?.includes("Modific") ? "bg-amber-500" : "bg-emerald-500"
                          }`} />
                          <span className="text-slate-400 truncate" title={sent.vigencia_info?.detalle}>
                            {sent.vigencia_info?.estado || "Sin registro"} - {sent.vigencia_info?.detalle?.substring(0, 20)}...
                          </span>
                        </div>
                      </div>

                      <button
                        onClick={() => {
                          setPrecedenteSeleccionado(index);
                          setSidepanelAbierto(true);
                        }}
                        className="w-full py-2.5 px-4 rounded bg-sky-600/10 hover:bg-sky-600 text-sky-400 hover:text-white border border-sky-500/20 hover:border-sky-500 text-xs font-bold transition-all duration-200 cursor-pointer flex items-center justify-center gap-1.5"
                      >
                        🔍 Ver Análisis de Similitud
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Informe de IA */}
            <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl space-y-6 backdrop-blur-sm shadow-xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <h4 className="text-lg font-bold flex items-center gap-2 text-purple-400">
                  🤖 Análisis Inteligente del Caso (Gemini AI)
                </h4>
                {explicacionIa && !explicacionIa.error && (
                  <span className="bg-purple-500/10 text-purple-400 text-xs px-2.5 py-1 rounded-full border border-purple-500/20 font-medium">
                    Análisis Estructurado
                  </span>
                )}
              </div>

              {cargandoIa ? (
                <div className="flex flex-col items-center justify-center py-8 space-y-3">
                  <div className="relative w-12 h-12">
                    <div className="absolute inset-0 border-4 border-purple-500/20 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-t-purple-500 rounded-full animate-spin"></div>
                  </div>
                  <p className="text-sm text-slate-400 animate-pulse font-medium">
                    La Inteligencia Artificial está analizando los hechos, cálculo de liquidación y jurisprudencia...
                  </p>
                </div>
              ) : explicacionIa ? (
                <div className="space-y-6">
                  {/* Resumen Principal */}
                  <div className={`p-5 rounded-xl border flex items-start gap-4 ${
                    explicacionIa.error 
                      ? "bg-red-950/15 border-red-500/20 text-red-300" 
                      : "bg-gradient-to-r from-purple-950/20 to-indigo-950/20 border-purple-500/25 text-purple-100"
                  }`}>
                    <div className={`p-2 rounded-lg text-lg flex items-center justify-center mt-0.5 ${
                      explicacionIa.error ? "bg-red-500/10" : "bg-purple-500/10"
                    }`}>
                      {explicacionIa.error ? "⚠️" : "💡"}
                    </div>
                    <div className="space-y-1">
                      <p className="text-xs font-semibold uppercase tracking-wider text-purple-400">Resumen del caso</p>
                      <p className="text-base font-medium leading-relaxed">{explicacionIa.resumen}</p>
                    </div>
                  </div>

                  {/* Cuerpo del diagnóstico en dos tarjetas */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Tarjeta 1: Significado */}
                    <div className="bg-slate-900 border border-slate-800 hover:border-violet-500/30 transition-all duration-300 p-5 rounded-xl space-y-3 shadow-md flex flex-col justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-violet-400 font-semibold text-sm">
                          <span className="p-1.5 rounded-lg bg-violet-500/10 text-base">⚖️</span>
                          ¿Qué significa esto para ti?
                        </div>
                        <p className="text-sm text-slate-300 leading-relaxed font-normal">
                          {explicacionIa.significado}
                        </p>
                      </div>
                    </div>

                    {/* Tarjeta 2: Análisis Detalle */}
                    <div className={`bg-slate-900 border border-slate-800 transition-all duration-300 p-5 rounded-xl space-y-3 shadow-md flex flex-col justify-between ${
                      diagnostico?.liquidacion 
                        ? "hover:border-emerald-500/30" 
                        : "hover:border-cyan-500/30"
                    }`}>
                      <div className="space-y-2">
                        <div className={`flex items-center gap-2 font-semibold text-sm ${
                          diagnostico?.liquidacion ? "text-emerald-400" : "text-cyan-400"
                        }`}>
                          <span className={`p-1.5 rounded-lg text-base ${
                            diagnostico?.liquidacion ? "bg-emerald-500/10" : "bg-cyan-500/10"
                          }`}>
                            {diagnostico?.liquidacion ? "💰" : "👔"}
                          </span>
                          {diagnostico?.liquidacion ? "Análisis de Beneficios y CTS" : "Estabilidad y Reincorporación"}
                        </div>
                        <p className="text-sm text-slate-300 leading-relaxed font-normal">
                          {explicacionIa.analisis_detalle}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Pasos sugeridos / Línea de tiempo */}
                  <div className="bg-slate-900/40 border border-slate-800 p-5 rounded-xl space-y-4">
                    <h5 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <span className="p-1 rounded-md bg-slate-850">📋</span>
                      Pasos sugeridos a seguir
                    </h5>
                    
                    <div className="relative pl-6 border-l border-slate-800 space-y-6">
                      {explicacionIa.pasos_sugeridos && explicacionIa.pasos_sugeridos.map((paso, idx) => (
                        <div key={idx} className="relative group">
                          {/* Círculo número */}
                          <div className="absolute -left-[39px] top-0.5 w-6 h-6 rounded-full bg-gradient-to-b from-purple-500 to-indigo-600 border border-slate-900 text-white flex items-center justify-center text-xs font-bold shadow-md transition-all group-hover:scale-110 duration-200">
                            {idx + 1}
                          </div>
                          <div className="space-y-1">
                            <p className="text-sm text-slate-300 leading-relaxed font-normal group-hover:text-slate-100 transition-colors duration-200">
                              {paso}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-6 text-center space-y-2">
                  <div className="text-2xl text-slate-600">🗝️</div>
                  <p className="text-sm text-slate-400 max-w-sm">
                    Ingresa tu API Key de Gemini en la barra lateral para recibir un resumen y recomendación inteligente de este caso.
                  </p>
                </div>
              )}
            </div>

            {/* Botones de acción final */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-850 pt-6">
              <button
                onClick={() => setPaso(1)}
                className="bg-slate-800 hover:bg-slate-750 text-slate-300 font-bold py-3 px-6 rounded-lg border border-slate-700"
              >
                ⬅️ Modificar Datos del Caso
              </button>
              <button
                onClick={descargarPdf}
                disabled={cargandoPdf}
                className="bg-gradient-to-r from-sky-500 to-sky-600 hover:from-sky-400 hover:to-sky-500 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:shadow-sky-500/20 disabled:opacity-50 flex justify-center items-center gap-2"
              >
                {cargandoPdf ? "Generando PDF..." : "Descargar Reporte en PDF 📄"}
              </button>
            </div>
          </section>
        )}

      </main>

      {/* Side Panel / Offcanvas Drawer for Precedent Detail */}
      {diagnostico && (
        <>
          {/* Backdrop overlay with blur */}
          <div 
            className={`fixed inset-0 bg-black/70 backdrop-blur-sm z-40 transition-opacity duration-300 ${
              sidepanelAbierto ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
            }`}
            onClick={() => setSidepanelAbierto(false)}
          />

          {/* Drawer container */}
          <div 
            className={`fixed inset-y-0 right-0 z-50 w-full max-w-2xl bg-slate-950 border-l border-slate-800 shadow-2xl flex flex-col justify-between transform transition-transform duration-300 ease-in-out ${
              sidepanelAbierto ? "translate-x-0" : "translate-x-full"
            }`}
          >
            {/* Header */}
            <div className="p-6 border-b border-slate-850 space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className="p-1.5 rounded-lg bg-sky-500/10 text-sky-400 text-sm">🏛️</span>
                  <h4 className="text-base font-bold text-slate-100 uppercase tracking-wide">
                    Análisis de Precedente
                  </h4>
                </div>
                <button 
                  onClick={() => setSidepanelAbierto(false)}
                  className="p-2 rounded-lg hover:bg-slate-900 text-slate-400 hover:text-slate-100 transition-colors duration-200 text-sm cursor-pointer"
                >
                  ✕ Cerrar
                </button>
              </div>

              {/* Tabs for selecting case inside the drawer */}
              <div className="flex bg-slate-900/60 p-1 rounded-lg border border-slate-900">
                {diagnostico.sentencias.map((s, idx) => (
                  <button
                    key={idx}
                    onClick={() => setPrecedenteSeleccionado(idx)}
                    className={`flex-1 text-center py-2 text-xs font-bold rounded-md transition-all duration-200 cursor-pointer ${
                      precedenteSeleccionado === idx 
                        ? "bg-sky-600 text-white shadow" 
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Caso {idx + 1}
                  </button>
                ))}
              </div>
            </div>

            {/* Content Body */}
            {diagnostico.sentencias[precedenteSeleccionado] && (() => {
              const activeSent = diagnostico.sentencias[precedenteSeleccionado];
              
              // Fallo styling
              let colorFallo = "text-slate-400 border-slate-800 bg-slate-950/40";
              let falloLabel = "Criterio Judicial";
              const textLower = (activeSent.titulo + " " + activeSent.abstract).toLowerCase();
              if (textLower.includes("infundada")) {
                colorFallo = "text-rose-400 border-rose-500/20 bg-rose-950/20";
                falloLabel = "Infundada (A favor del empleador)";
              } else if (textLower.includes("fundada") || textLower.includes("fundado")) {
                colorFallo = "text-emerald-400 border-emerald-500/20 bg-emerald-950/20";
                falloLabel = "Fundada (A favor del trabajador)";
              } else if (textLower.includes("improcedente")) {
                colorFallo = "text-slate-400 border-slate-700/20 bg-slate-850/20";
                falloLabel = "Improcedente (Aspecto formal)";
              }

              // Vigencia styling
              let colorVigencia = "text-emerald-400 bg-emerald-950/40 border-emerald-500/20";
              if (activeSent.vigencia_info?.estado?.includes("Derog")) {
                colorVigencia = "text-rose-400 bg-rose-950/40 border-rose-500/20";
              } else if (activeSent.vigencia_info?.estado?.includes("Modific")) {
                colorVigencia = "text-amber-400 bg-amber-950/40 border-amber-500/20";
              }

              return (
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  {/* Ficha Técnica Metadata */}
                  <div className="bg-slate-900 border border-slate-850 p-4 rounded-xl space-y-3 shadow-md">
                    <h5 className="text-sm font-bold text-slate-100">{activeSent.titulo}</h5>
                    
                    <div className="grid grid-cols-2 gap-3 pt-2 text-xs">
                      <div className="space-y-1">
                        <span className="text-slate-500 block">Similitud Factual</span>
                        <span className="text-sky-400 font-bold text-sm">{(activeSent.similitud * 100).toFixed(1)}% de coincidencia</span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-slate-500 block">Sentido de Decisión</span>
                        <span className={`inline-block font-semibold px-2 py-0.5 rounded border text-[10px] ${colorFallo}`}>
                          {falloLabel}
                        </span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-slate-500 block">Estado de Norma Citada</span>
                        <span className={`inline-block font-semibold px-2 py-0.5 rounded border text-[10px] ${colorVigencia}`}>
                          {activeSent.vigencia_info?.estado || "Sin registro"}
                        </span>
                      </div>
                      <div className="space-y-1">
                        <span className="text-slate-500 block">Fecha/Región del Fallo</span>
                        <span className="text-slate-300 font-semibold">{activeSent.fecha || "No disponible"}</span>
                      </div>
                    </div>

                    {activeSent.vigencia_info?.detalle && (
                      <p className="text-[10px] text-slate-400 border-t border-slate-800 pt-2 italic leading-relaxed">
                        📍 <strong>Nota de El Peruano:</strong> {activeSent.vigencia_info.detalle}
                      </p>
                    )}
                  </div>

                  {/* Document Paper Container */}
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-400 block uppercase tracking-wider">
                      📄 Vista del Folio / Abstract Resaltado:
                    </label>
                    <div className="bg-white text-slate-800 p-8 rounded-xl shadow-inner font-serif leading-relaxed text-sm border-l-4 border-amber-300 relative select-text">
                      {/* Sello Judicial Mock */}
                      <div className="absolute top-4 right-4 text-[9px] font-sans font-bold border-2 border-red-500/30 text-red-500/40 uppercase tracking-widest px-2 py-1 transform rotate-12 select-none pointer-events-none">
                        Expediente Judicial
                      </div>
                      <p className="whitespace-pre-line text-justify leading-relaxed">
                        {renderTextoResaltado(activeSent.abstract)}
                      </p>
                    </div>
                  </div>

                  {/* Fundamento Legal Citado (El Peruano) */}
                  {activeSent.articulo_info && (
                    <div className="bg-slate-900 border border-slate-850 p-5 rounded-xl space-y-3">
                      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
                        <span className="text-base">📖</span>
                        <h6 className="text-xs font-bold text-slate-200">
                          Fundamento Legal Citado: {activeSent.articulo_info.titulo_norma} (Art. {activeSent.articulo_info.num_articulo})
                        </h6>
                      </div>
                      <p className="text-[11px] text-slate-400 italic">"{activeSent.articulo_info.sumilla}"</p>
                      <blockquote className="border-l-2 border-sky-500 pl-3 text-slate-300 font-mono text-xs bg-slate-950/40 p-3 rounded">
                        {renderTextoResaltado(activeSent.articulo_info.texto_articulo)}
                      </blockquote>
                    </div>
                  )}
                </div>
              );
            })()}

            {/* Footer containing action buttons */}
            {diagnostico.sentencias[precedenteSeleccionado] && (
              <div className="p-4 border-t border-slate-850 bg-slate-950 flex gap-3">
                <a
                  href={diagnostico.sentencias[precedenteSeleccionado].url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 py-3 px-4 bg-gradient-to-r from-sky-500 to-sky-600 hover:from-sky-400 hover:to-sky-500 text-white font-bold rounded-lg text-xs text-center shadow-md transition-all duration-200 cursor-pointer"
                >
                  📄 Descargar Expediente Completo (PDF Oficial) ↗️
                </a>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
