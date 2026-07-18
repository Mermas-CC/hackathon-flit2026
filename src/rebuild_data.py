import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer

def rebuild():
    parquet_path = "data/sentencias_desnat.parquet"
    embeddings_path = "data/embeddings.npy"
    
    print("Leyendo sentencias_desnat.parquet...")
    df = pd.read_parquet(parquet_path)
    print(f"Total registros originales: {len(df)}")
    
    # Re-filtrar por metadata_pretension que contenga o sea exactamente 'Desnaturalización de Contrato'
    # para evitar ruidos de familia, alimentos, etc.
    print("Filtrando casos de desnaturalización reales...")
    df_clean = df[df['metadata_pretension'].str.contains('Desnaturalización de Contrato', na=False, case=False)].copy()
    
    # Restablecer el índice
    df_clean = df_clean.reset_index(drop=True)
    print(f"Total registros limpios: {len(df_clean)}")
    
    # Cargar SBERT
    print("Cargando modelo SBERT (hiiamsid/sentence_similarity_spanish_es)...")
    model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')
    
    # Generar embeddings sobre abstract_clean
    print("Generando nuevos embeddings vectoriales...")
    texts = df_clean['abstract_clean'].fillna(df_clean['abstract']).fillna("").tolist()
    new_embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    new_embeddings = new_embeddings.astype(np.float32)
    
    # Guardar ambos archivos alineados
    print(f"Guardando nuevo parquet limpio: {parquet_path}...")
    df_clean.to_parquet(parquet_path, index=False)
    
    print(f"Guardando nuevos embeddings alineados: {embeddings_path}...")
    np.save(embeddings_path, new_embeddings)
    
    print("=== RE-ALINEACIÓN COMPLETADA CON ÉXITO ===")

if __name__ == "__main__":
    rebuild()
