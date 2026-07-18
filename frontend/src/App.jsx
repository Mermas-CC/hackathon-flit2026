import React, { useState } from 'react';

export default function App() {
  // Estados del Wizard
  const [paso, setPaso] = useState(1);
  const [apiKey, setApiKey] = useState("AIzaSyAaguhbIjqNOE_xlT91WJF9ZLqBuSK17oA");
  
  // Datos del Caso (Valores predeterminados para debug "Next, Next")
  const [regimen, setRegimen] = useState("Privado (DL 728)");
  const [fechaInicio, setFechaInicio] = useState("2021-06-01");
  const [fechaCese, setFechaCese] = useState("2023-06-01");
  const [sueldo, setSueldo] = useState(4000.0);
  const [resumenHechos, setResumenHechos] = useState(
    "Trabajé como asistente administrativo con recibos por honorarios, tenía un jefe directo que controlaba mi horario y usaba la laptop de la empresa."
  );
  const [esObreroMunicipal, setEsObreroMunicipal] = useState(false);

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
  const [explicacionIa, setExplicacionIa] = useState("");
  const [cargandoDiagnostico, setCargandoDiagnostico] = useState(false);
  const [cargandoIa, setCargandoIa] = useState(false);
  const [cargandoPdf, setCargandoPdf] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

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

  // 1. Llamar al Diagnóstico
  const ejecutarDiagnostico = async () => {
    setCargandoDiagnostico(true);
    setErrorMsg("");
    try {
      const response = await fetch("http://localhost:8000/api/diagnostico", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          regimen,
          fecha_inicio: fechaInicio,
          fecha_cese: fechaCese,
          sueldo: parseFloat(sueldo),
          resumen_hechos: resumenHechos,
          es_obrero_municipal: esObreroMunicipal,
          respuestas_scorecard: respuestasScorecard
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
      const response = await fetch("http://localhost:8000/api/explicar-ia", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          api_key: apiKey,
          datos_usuario: {
            regimen,
            fecha_inicio: fechaInicio,
            fecha_cese: fechaCese,
            sueldo: parseFloat(sueldo),
            resumen_hechos: resumenHechos
          },
          scorecard_info: diagData.scorecard,
          liquidacion: diagData.liquidacion,
          sentencias: diagData.sentencias
        })
      });
      const data = await response.json();
      setExplicacionIa(data.explicacion);
    } catch (e) {
      setExplicacionIa(`Error al generar análisis con IA: ${e.message}`);
    } finally {
      setCargandoIa(false);
    }
  };

  // 3. Descargar Reporte PDF
  const descargarPdf = async () => {
    setCargandoPdf(true);
    try {
      const response = await fetch("http://localhost:8000/api/reporte-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          datos_usuario: {
            regimen,
            fecha_inicio: fechaInicio,
            fecha_cese: fechaCese,
            sueldo: parseFloat(sueldo),
            resumen_hechos: resumenHechos,
            es_obrero_municipal: esObreroMunicipal
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
            ⚖️ DesnaturalizaCheck
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

            <div className="glass-panel p-6 rounded-2xl space-y-4 division-y division-slate-800">
              {preguntas.map((p) => (
                <div key={p.key} className="py-3 flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
                  <span className="text-sm font-medium text-slate-200">{p.label}</span>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name={p.key}
                        value="Sí"
                        checked={respuestasScorecard[p.key] === "Sí"}
                        onChange={() => handleScorecardChange(p.key, "Sí")}
                        className="w-4 h-4 text-sky-500 border-slate-700 bg-slate-900 focus:ring-sky-500"
                      />
                      <span className="text-sm">Sí</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name={p.key}
                        value="No"
                        checked={respuestasScorecard[p.key] === "No"}
                        onChange={() => handleScorecardChange(p.key, "No")}
                        className="w-4 h-4 text-sky-500 border-slate-700 bg-slate-900 focus:ring-sky-500"
                      />
                      <span className="text-sm">No</span>
                    </label>
                  </div>
                </div>
              ))}
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

              <div className="space-y-4">
                {diagnostico.sentencias.map((sent, index) => {
                  // Colores del fallo
                  let colorFallo = "text-slate-400 border-slate-800 bg-slate-950/40";
                  let falloLabel = "Criterio Judicial";
                  
                  const textLower = (sent.titulo + " " + sent.abstract).toLowerCase();
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
                  
                  // Color del semáforo de vigencia de El Peruano
                  let colorVigencia = "text-emerald-400 bg-emerald-950/40 border-emerald-500/20";
                  if (sent.vigencia_info?.estado?.includes("Derog")) {
                    colorVigencia = "text-rose-400 bg-rose-950/40 border-rose-500/20";
                  } else if (sent.vigencia_info?.estado?.includes("Modific")) {
                    colorVigencia = "text-amber-400 bg-amber-950/40 border-amber-500/20";
                  }

                  return (
                    <div key={index} className="glass-panel p-5 rounded-xl space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <h5 className="font-bold text-sky-400 text-sm">
                            Caso {index + 1}: {sent.titulo}
                          </h5>
                          <span className="text-[10px] text-slate-500">Coincidencia: {(sent.similitud * 100).toFixed(1)}%</span>
                        </div>
                        <span className={`text-[10px] font-bold px-2 py-1 rounded border ${colorFallo}`}>
                          {falloLabel}
                        </span>
                      </div>
                      
                      {/* Estado Ley El Peruano */}
                      <div className="flex items-center gap-2 text-xs">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${colorVigencia}`}>
                          {sent.vigencia_info?.estado}
                        </span>
                        <span className="text-slate-400 text-[11px]">
                          {sent.vigencia_info?.detalle}
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed">
                        {sent.abstract.substring(0, 320)}...
                      </p>
                      
                      <div className="flex justify-between items-center pt-2">
                        <a 
                          href={sent.url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="text-xs text-sky-400 font-bold hover:underline"
                        >
                          📄 Descargar Expediente Completo (PDF Oficial) ↗️
                        </a>
                      </div>

                      {/* Expansor del artículo citador */}
                      {sent.articulo_info && (
                        <div className="bg-slate-950/40 rounded-lg p-3 border border-slate-800/80 text-xs">
                          <p className="font-bold text-slate-300 mb-1">
                            📖 Fundamento legal citado: {sent.articulo_info.titulo_norma} - {sent.articulo_info.num_articulo}
                          </p>
                          <p className="text-[11px] text-slate-400 italic mb-2">"{sent.articulo_info.sumilla}"</p>
                          <blockquote className="border-l-2 border-sky-500 pl-2 text-slate-300 font-mono text-[11px]">
                            {sent.articulo_info.texto_articulo}
                          </blockquote>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Informe de IA */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
              <h4 className="text-lg font-bold flex items-center gap-2 text-purple-400">
                🤖 Explicación del Caso por IA (Gemini 2.5)
              </h4>
              {cargandoIa ? (
                <div className="text-sm text-slate-400 flex items-center gap-2">
                  <span className="animate-pulse">●</span> Redactando análisis amigable...
                </div>
              ) : explicacionIa ? (
                <div className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {explicacionIa}
                </div>
              ) : (
                <p className="text-xs text-slate-500">
                  Ingresa tu API Key en la barra lateral para ver la explicación por IA del caso.
                </p>
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
    </div>
  );
}
