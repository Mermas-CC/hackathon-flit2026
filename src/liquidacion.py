import datetime
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class DetalleLiquidacion:
    cts_reclamable: float
    cts_prescrito: float
    gratif_reclamable: float
    gratif_prescrito: float
    vac_reclamable: float
    vac_prescrito: float
    bonif_reclamable: float
    bonif_prescrito: float
    interes_reclamable: float
    interes_prescrito: float
    total_reclamable: float
    total_prescrito: float
    dias_totales: int
    meses_totales: float
    prescrito_totalmente: bool
    dias_desde_cese: int

def calcular_liquidacion_728(
    fecha_inicio: datetime.date,
    fecha_cese: datetime.date,
    sueldo: float,
    dias_vacaciones_tomadas: int = 0,
    cts_ya_pagada: float = 0.0,
    gratif_ya_pagada: float = 0.0,
    fecha_calculo: datetime.date = None
) -> DetalleLiquidacion:
    if fecha_calculo is None:
        fecha_calculo = datetime.date.today()
        
    dias_totales = (fecha_cese - fecha_inicio).days
    if dias_totales < 0:
        dias_totales = 0
    
    # Calcular meses totales aproximados
    meses_totales = dias_totales / 30.0
    
    # Verificar prescripción laboral (Ley 27321: 4 años desde el cese)
    dias_desde_cese = (fecha_calculo - fecha_cese).days
    anios_desde_cese = dias_desde_cese / 365.25
    prescrito_totalmente = anios_desde_cese > 4.0
    
    # 1. CTS Computable (sueldo + 1/6 gratificación)
    base_cts = sueldo + (sueldo / 6.0)
    cts_bruta = base_cts * (meses_totales / 12.0)
    cts_teorica = max(0.0, cts_bruta - cts_ya_pagada)
    
    # 2. Gratificaciones (1 sueldo completo por cada semestre)
    gratif_bruta = (sueldo * 2.0) * (meses_totales / 12.0)
    gratif_teorica = max(0.0, gratif_bruta - gratif_ya_pagada)
    bonif_teorica = gratif_teorica * 0.09
    
    # 3. Vacaciones (30 días por año de labores = 2.5 días por mes)
    dias_vacaciones_generados = meses_totales * 2.5
    dias_vacaciones_reclamables = max(0.0, dias_vacaciones_generados - dias_vacaciones_tomadas)
    vac_teorica = (sueldo / 30.0) * dias_vacaciones_reclamables
    
    capital_total = cts_teorica + gratif_teorica + vac_teorica + bonif_teorica
    
    # 4. Interés Legal Laboral (Decreto Ley 25920)
    if dias_desde_cese > 0:
        tasa_periodo = 0.03 * (dias_desde_cese / 365.25)
        interes_teorico = capital_total * tasa_periodo
    else:
        interes_teorico = 0.0
        
    if prescrito_totalmente:
        return DetalleLiquidacion(
            cts_reclamable=0.0,
            cts_prescrito=round(cts_teorica, 2),
            gratif_reclamable=0.0,
            gratif_prescrito=round(gratif_teorica, 2),
            vac_reclamable=0.0,
            vac_prescrito=round(vac_teorica, 2),
            bonif_reclamable=0.0,
            bonif_prescrito=round(bonif_teorica, 2),
            interes_reclamable=0.0,
            interes_prescrito=round(interes_teorico, 2),
            total_reclamable=0.0,
            total_prescrito=round(capital_total + interes_teorico, 2),
            dias_totales=dias_totales,
            meses_totales=round(meses_totales, 2),
            prescrito_totalmente=True,
            dias_desde_cese=dias_desde_cese
        )
    else:
        return DetalleLiquidacion(
            cts_reclamable=round(cts_teorica, 2),
            cts_prescrito=0.0,
            gratif_reclamable=round(gratif_teorica, 2),
            gratif_prescrito=0.0,
            vac_reclamable=round(vac_teorica, 2),
            vac_prescrito=0.0,
            bonif_reclamable=round(bonif_teorica, 2),
            bonif_prescrito=0.0,
            interes_reclamable=round(interes_teorico, 2),
            interes_prescrito=0.0,
            total_reclamable=round(capital_total + interes_teorico, 2),
            total_prescrito=0.0,
            dias_totales=dias_totales,
            meses_totales=round(meses_totales, 2),
            prescrito_totalmente=False,
            dias_desde_cese=dias_desde_cese
        )

def obtener_mensaje_regimen_publico(es_obrero_municipal: bool = False) -> Dict[str, Any]:
    advertencia = (
        "**IMPORTANTE (Precedente Huatuco):** De acuerdo al precedente vinculante de la Casación 5057-2013-Junín, "
        "para que un trabajador del sector público sea reincorporado bajo contrato indeterminado, se requiere obligatoriamente "
        "que haya ingresado por concurso público de méritos en una plaza presupuestada y vacante de naturaleza permanente."
    )
    
    excepcion = ""
    if es_obrero_municipal:
        excepcion = (
            "**EXCEPCIÓN APLICABLE:** Al declarar que es *obrero municipal*, por ley se encuentra excluido del precedente Huatuco "
            "(según la jurisprudencia del Tribunal Constitucional), por lo cual puede solicitar su reincorporación al amparo del régimen privado (DL 728)."
        )
    else:
        excepcion = (
            "**Excepciones comunes:** El precedente Huatuco no se aplica a obreros municipales, personal de confianza, cargos políticos "
            "o regímenes artísticos y de carreras especiales con regulación propia."
        )
        
    return {
        "consecuencia": "La desnaturalización bajo la Ley 24041 otorga el derecho a la **Reincorporación laboral** (estabilidad), no al cobro directo de beneficios del régimen laboral privado DL 728.",
        "advertencia_huatuco": advertencia,
        "excepciones": excepcion
    }

def obtener_mensaje_cas() -> Dict[str, Any]:
    return {
        "consecuencia": "La desnaturalización de contratos CAS consecutivos o contratos de locación encubiertos como CAS otorga el derecho a la **estabilidad laboral** en la entidad pública, sujeta a las reglas del precedente Huatuco.",
        "advertencia": "Si el cese fue injustificado, se puede solicitar la reposición en el puesto o el pago de la indemnización por despido arbitrario de acuerdo a las normas del régimen CAS."
    }
