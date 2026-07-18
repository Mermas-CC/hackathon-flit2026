import os
import numpy as np
import pandas as pd
import duckdb
from typing import List, Dict, Any

class SentenciasRetrieval:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Obtener el directorio raíz del proyecto dinámicamente
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            
        self.parquet_path = os.path.join(data_dir, "sentencias_desnat.parquet")
        self.npy_path = os.path.join(data_dir, "embeddings.npy")
        
        # Cargar embeddings
        if not os.path.exists(self.npy_path):
            raise FileNotFoundError(f"No se encontró el archivo de embeddings en {self.npy_path}. Ejecuta data_prep.py primero.")
        self.embeddings = np.load(self.npy_path).astype(np.float32) # Convertir a float32 para cálculos
        
        # Cargar dataframe de sentencias
        if not os.path.exists(self.parquet_path):
            raise FileNotFoundError(f"No se encontró el archivo Parquet en {self.parquet_path}. Ejecuta data_prep.py primero.")
        self.df = pd.read_parquet(self.parquet_path)
        
        # Inicializar modelo SBERT
        from sentence_transformers import SentenceTransformer
        self.model_name = "hiiamsid/sentence_similarity_spanish_es"
        self.model = SentenceTransformer(self.model_name)
        
        # Inicializar conexión de DuckDB
        self.con = duckdb.connect(database=':memory:')
        self.con.register('sentencias', self.df)

    def search(self, query: str, regimen: str, top_k: int = 3) -> List[Dict[str, Any]]:
        # Generar embedding para la consulta del usuario
        query_emb = self.model.encode(query, convert_to_numpy=True).astype(np.float32)
        
        # Calcular similitud coseno usando NumPy
        query_norm = np.linalg.norm(query_emb)
        if query_norm == 0:
            query_norm = 1e-9
            
        norms = np.linalg.norm(self.embeddings, axis=1)
        norms = np.where(norms == 0, 1e-9, norms)
        
        similarities = np.dot(self.embeddings, query_emb) / (norms * query_norm)
        
        # Agregar similitudes al dataframe local
        df_temp = self.df.copy()
        df_temp['similarity'] = similarities
        
        # Registrar tabla temporal en DuckDB
        self.con.register('sentencias_temp', df_temp)
        
        # Mapeo del régimen seleccionado a las categorías en la base de datos
        # Opciones esperadas: 'Privado (DL 728)', 'Público (Ley 24041 / DL 276)', 'CAS (DL 1057)'
        query_sql = f"""
            SELECT ID, titulo, abstract_clean, metadata_pretension, regimen, similarity, url_pdf, metadata_norma_derecho, fecha
            FROM sentencias_temp
            WHERE regimen = '{regimen}'
            ORDER BY similarity DESC
            LIMIT {top_k}
        """
        
        result_df = self.con.execute(query_sql).fetchdf()
        
        results = []
        for _, row in result_df.iterrows():
            results.append({
                "id": row['ID'],
                "titulo": row['titulo'],
                "abstract": row['abstract_clean'],
                "pretension": row['metadata_pretension'],
                "regimen": row['regimen'],
                "similitud": float(row['similarity']),
                "url": row['url_pdf'],
                "norma_derecho": row['metadata_norma_derecho'] if pd.notna(row['metadata_norma_derecho']) else "Ley 24041",
                "fecha": str(row['fecha']) if pd.notna(row['fecha']) else "2020-01-01"
            })
            
        return results
