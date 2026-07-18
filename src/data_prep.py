import os
import re
import json
import glob
import pandas as pd
import numpy as np

def clean_and_anonimize(text):
    if not isinstance(text, str):
        return ""
    # Anonimizar DNI (8 dígitos)
    text = re.sub(r'\b\d{8}\b', '[DNI]', text)
    # Patrones comunes de nombres
    text = re.sub(r'(?:Sra?\.|don|doña|contra|demandante|demandado)\s+([A-ZÁÉÍÓÚÑ][a-zñáéíóú]+(?:\s+[A-ZÁÉÍÓÚÑ][a-zñáéíóú]+){1,3})', r'\1 [ANONIMIZADO]', text)
    return text

def detect_regimen(row):
    text = f"{row.get('metadata_pretension', '')} {row.get('abstract', '')}".lower()
    
    # Prioridad CAS
    if any(k in text for k in ['cas', '1057', 'administrativo de servicios']):
        return 'CAS (DL 1057)'
    # Prioridad Ley 24041 / 276
    elif any(k in text for k in ['24041', '276', 'público', 'carrera administrativa', 'servidor público']):
        return 'Público (Ley 24041 / DL 276)'
    # Por defecto / DL 728
    else:
        return 'Privado (DL 728)'

def main():
    json_path = "/Users/mac-mermitas/Documents/INVESTIGACION/FINE TUNING/LEGAL/data/raw/poder_judicial_data_completa.json"
    dest_dir = "/Users/mac-mermitas/Documents/HACKATON/data"
    os.makedirs(dest_dir, exist_ok=True)
    
    # 1. Cargar dataset base
    print(f"Leyendo archivo JSON base desde {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Base de datos cargada: {len(df)} registros.")
    
    # Filtrar por desnaturalización
    df['abstract'] = df['abstract'].fillna("")
    df['metadata_pretension'] = df['metadata_pretension'].fillna("")
    
    kw_pattern = r'(desnaturaliza|locaci.n de servicios|contrato de locaci.n|cas\b|contrato administrativo de servicios|24041)'
    mask = (
        df['metadata_pretension'].str.contains(kw_pattern, case=False, regex=True) |
        df['abstract'].str.contains(kw_pattern, case=False, regex=True)
    )
    df_filtered = df[mask].copy()
    df_filtered = df_filtered[df_filtered['abstract'].str.strip() != ""]
    print(f"Registros de desnaturalización filtrados (base): {len(df_filtered)}")
    
    # 2. Cargar y fusionar nuevos datos del scraper
    nuevas_sentencias_files = glob.glob(os.path.join(dest_dir, "nuevas_sentencias_*.json"))
    nuevos_registros = []
    
    for file_path in nuevas_sentencias_files:
        print(f"Encontrado archivo de nuevas sentencias: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                nuevos_datos = json.load(f)
                nuevos_registros.extend(nuevos_datos)
        except Exception as e:
            print(f"Error al leer {file_path}: {e}")
            
    if nuevos_registros:
        df_nuevos = pd.DataFrame(nuevos_registros)
        df_nuevos['abstract'] = df_nuevos['abstract'].fillna("")
        df_nuevos['metadata_pretension'] = df_nuevos['metadata_pretension'].fillna("")
        
        # Unir
        df_filtered = pd.concat([df_filtered, df_nuevos], ignore_index=True)
        # Quitar duplicados por ID o título
        df_filtered = df_filtered.drop_duplicates(subset=['titulo'], keep='last')
        print(f"Total registros tras la fusión con datos del scraper: {len(df_filtered)}")
        
    # 3. Limpieza y categorización
    df_filtered['abstract_clean'] = df_filtered['abstract'].apply(clean_and_anonimize)
    df_filtered['regimen'] = df_filtered.apply(detect_regimen, axis=1)
    
    # Guardar a Parquet
    parquet_path = os.path.join(dest_dir, "sentencias_desnat.parquet")
    df_filtered.to_parquet(parquet_path, index=False)
    print(f"Archivo Parquet actualizado guardado en {parquet_path}")
    
    # 4. Generar / Actualizar Embeddings
    print("Iniciando generación/actualización de embeddings con SBERT...")
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "sentence-transformers"])
        from sentence_transformers import SentenceTransformer
        
    model_name = "hiiamsid/sentence_similarity_spanish_es"
    model = SentenceTransformer(model_name)
    
    texts = df_filtered['abstract_clean'].tolist()
    print(f"Calculando embeddings para {len(texts)} textos en total...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Guardar como float16
    embeddings_half = embeddings.astype(np.float16)
    npy_path = os.path.join(dest_dir, "embeddings.npy")
    np.save(npy_path, embeddings_half)
    print(f"Embeddings actualizados guardados en {npy_path} con forma {embeddings_half.shape}")

if __name__ == "__main__":
    main()
