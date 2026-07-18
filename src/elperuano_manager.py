import pandas as pd
import datetime
from typing import Dict, Any, List, Optional

# Base de datos local curada de respaldo (Garantiza que la demo funcione al 100% si los parquets grandes están corruptos)
FALLBACK_NORMAS = [
    {
        "num_norma": "24041",
        "titulo_norma": "Ley N° 24041",
        "sumilla": "Servidores públicos contratados para labores de naturaleza permanente que tengan más de un año de servicios ininterrumpidos.",
        "fecha_publicacion": "1984-12-28"
    },
    {
        "num_norma": "728",
        "titulo_norma": "Decreto Legislativo N° 728",
        "sumilla": "Ley de Productividad y Competitividad Laboral (Régimen Privado).",
        "fecha_publicacion": "1997-03-27"
    },
    {
        "num_norma": "25920",
        "titulo_norma": "Decreto Ley N° 25920",
        "sumilla": "Reglas de cálculo para el interés legal laboral por adeudos no pagados.",
        "fecha_publicacion": "1992-12-03"
    },
    {
        "num_norma": "27444",
        "titulo_norma": "Ley N° 27444",
        "sumilla": "Ley del Procedimiento Administrativo General.",
        "fecha_publicacion": "2001-04-11"
    },
    {
        "num_norma": "1057",
        "titulo_norma": "Decreto Legislativo N° 1057",
        "sumilla": "Régimen especial de Contratación Administrativa de Servicios (CAS).",
        "fecha_publicacion": "2008-06-28"
    },
    {
        "num_norma": "27321",
        "titulo_norma": "Ley N° 27321",
        "sumilla": "Establece nuevo plazo de prescripción de las acciones nacidas de la relación laboral (4 años).",
        "fecha_publicacion": "2000-07-23"
    }
]

FALLBACK_ARTICULOS = [
    {
        "num_norma": "24041",
        "num_articulo": "Art. 1",
        "texto_articulo": "Los servidores públicos contratados para labores de naturaleza permanente, que tengan más de un año ininterrumpido de servicios, no pueden ser cesados ni despedidos sino por las causas previstas en el Capítulo V del Decreto Legislativo N° 276 y con sujeción al procedimiento administrativo."
    },
    {
        "num_norma": "728",
        "num_articulo": "Art. 4",
        "texto_articulo": "En toda prestación personal de servicios remunerados y subordinados, se presume la existencia de un contrato de trabajo a plazo indeterminado. El contrato individual de trabajo puede celebrarse libremente por tiempo indeterminado o sujeto a modalidad."
    },
    {
        "num_norma": "25920",
        "num_articulo": "Art. 3",
        "texto_articulo": "El interés legal en materia laboral no es capitalizable. Se devenga a partir del día siguiente de aquél en que se produjo el incumplimiento de la obligación del empleador hasta el día de su pago efectivo, sin necesidad de exigencia o reclamo."
    },
    {
        "num_norma": "1057",
        "num_articulo": "Art. 2",
        "texto_articulo": "El Contrato Administrativo de Servicios es un régimen especial de contratación laboral privativo del Estado. No se encuentra bajo el régimen de la carrera administrativa (DL 276) ni del régimen de la actividad privada (DL 728)."
    },
    {
        "num_norma": "27321",
        "num_articulo": "Art. Único",
        "texto_articulo": "Las acciones que nazcan de las relaciones de trabajo prescriben a los cuatro (4) años, computados desde el día siguiente en que se extingue la relación laboral."
    },
    {
        "num_norma": "27444",
        "num_articulo": "Art. 1",
        "texto_articulo": "El procedimiento administrativo se rige por los principios de legalidad, debido procedimiento, impulso de oficio, razonabilidad, imparcialidad y primacía del interés público."
    }
]

FALLBACK_VIGENCIA = [
    {
        "num_norma": "27444",
        "modificado_por": "Decreto Legislativo N° 1633",
        "fecha_modificacion": "2024-08-15",
        "tipo_cambio": "Modificado"
    },
    {
        "num_norma": "1057",
        "modificado_por": "Ley N° 31131",
        "fecha_modificacion": "2021-03-09",
        "tipo_cambio": "Modificado"
    },
    {
        "num_norma": "24041",
        "modificado_por": "Ley N° 31131",
        "fecha_modificacion": "2021-03-09",
        "tipo_cambio": "Derogado parcialmente"
    }
]

class ElPeruanoManager:
    """
    Administrador de la base de datos de El Peruano.
    Realiza la lectura de los parquets locales de elperuano o cae con elegancia
    al diccionario de fallback curado.
    """
    def __init__(self):
        self.normas = pd.DataFrame(FALLBACK_NORMAS)
        self.articulos = pd.DataFrame(FALLBACK_ARTICULOS)
        self.vigencia = pd.DataFrame(FALLBACK_VIGENCIA)
        self._intentar_cargar_parquets()

    def _intentar_cargar_parquets(self):
        # Intentamos cargar de archivos locales si existen y son válidos
        try:
            p_normas = "data/elperuano_laboral_normas.parquet"
            p_articulos = "data/elperuano_laboral_articulos.parquet"
            p_vigencia = "data/elperuano_laboral_vigencia.parquet"
            
            if os.path.exists(p_normas) and os.path.exists(p_articulos) and os.path.exists(p_vigencia):
                self.normas = pd.read_parquet(p_normas)
                self.articulos = pd.read_parquet(p_articulos)
                self.vigencia = pd.read_parquet(p_vigencia)
                print("ElPeruanoManager: Parquets específicos cargados exitosamente.")
        except Exception as e:
            print(f"ElPeruanoManager: Usando base de datos curada en memoria (Error al abrir parquets: {e})")

    def obtener_articulo_por_ley(self, ley_ref: str) -> Optional[Dict[str, Any]]:
        """
        Dada una referencia de ley (ej. 'Ley 24041', 'DL 728', '25920'), 
        busca y retorna el artículo principal relacionado.
        """
        # Extraer el número de la ley
        import re
        match = re.search(r'(\d+)', ley_ref)
        if not match:
            return None
        num_norma = match.group(1)
        
        # Buscar en normas
        norma_row = self.normas[self.normas['num_norma'] == num_norma]
        if norma_row.empty:
            return None
            
        norma_info = norma_row.iloc[0].to_dict()
        
        # Buscar el artículo
        articulo_row = self.articulos[self.articulos['num_norma'] == num_norma]
        if not articulo_row.empty:
            norma_info['num_articulo'] = articulo_row.iloc[0]['num_articulo']
            norma_info['texto_articulo'] = articulo_row.iloc[0]['texto_articulo']
        else:
            norma_info['num_articulo'] = "Art. General"
            norma_info['texto_articulo'] = "Texto de referencia laboral del sector público/privado."
            
        return norma_info

    def verificar_vigencia(self, ley_ref: str, fecha_sentencia_str: str) -> Dict[str, Any]:
        """
        Verifica el estado de vigencia de una ley respecto a la fecha de la sentencia.
        Retorna:
          - estado: '🟢 Vigente', '🟡 Modificada después', '🔴 Derogada'
          - detalle: Texto describiendo los cambios de vigencia
        """
        import re
        match = re.search(r'(\d+)', ley_ref)
        if not match:
            return {"estado": "🟢 Vigente", "detalle": "Norma laboral en vigencia plena."}
            
        num_norma = match.group(1)
        
        # Parsear fecha de la sentencia
        try:
            # Asumimos formato AAAA-MM-DD
            fecha_sentencia = pd.to_datetime(fecha_sentencia_str).date()
        except:
            fecha_sentencia = datetime.date(2015, 1, 1) # Fallback seguro
            
        # Buscar modificaciones en la tabla de vigencia
        modificaciones = self.vigencia[self.vigencia['num_norma'] == num_norma]
        if modificaciones.empty:
            return {
                "estado": "🟢 Vigente",
                "detalle": "Esta ley no registra modificaciones en el histórico laboral y sigue vigente."
            }
            
        # Evaluar la última modificación
        modificaciones = modificaciones.sort_values(by="fecha_modificacion", ascending=False)
        ultima_mod = modificaciones.iloc[0]
        fecha_mod = pd.to_datetime(ultima_mod['fecha_modificacion']).date()
        
        if fecha_sentencia > fecha_mod:
            # La sentencia es posterior a la modificación, por tanto el juez ya aplicó la ley modificada
            if "derog" in ultima_mod['tipo_cambio'].lower():
                return {
                    "estado": "🔴 Derogada",
                    "detalle": f"El fallo se dictó después de que la ley fuera derogada (Derogada el {fecha_mod} por {ultima_mod['modificado_por']})."
                }
            else:
                return {
                    "estado": "🟢 Vigente (Modificada)",
                    "detalle": f"El juez aplicó la ley sabiendo que ya fue modificada por {ultima_mod['modificado_por']}."
                }
        else:
            # La sentencia es anterior a la modificación, la ley cambió DESPUÉS de que el juez dio la sentencia
            if "derog" in ultima_mod['tipo_cambio'].lower():
                return {
                    "estado": "🔴 Derogada",
                    "detalle": f"¡Atención! La ley en la que se basó este fallo fue DEROGADA posteriormente (el {fecha_mod} por {ultima_mod['modificado_por']})."
                }
            else:
                return {
                    "estado": "🟡 Modificada después",
                    "detalle": f"Esta ley fue modificada con posterioridad a la sentencia (el {fecha_mod} por {ultima_mod['modificado_por']}). Revisa si el criterio se sostiene."
                }
import os
