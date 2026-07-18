import os
import time
import json
import re
from bs4 import BeautifulSoup

def main():
    print("=====================================================================")
    print("⚖️  BOILERPLATE SCRAPER - TRIBUNAL CONSTITUCIONAL DEL PERÚ")
    print("=====================================================================")
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright no está instalado. Instalando...")
        import subprocess
        subprocess.check_call(["pip", "install", "playwright"])
        subprocess.check_call(["playwright", "install"])
        from playwright.sync_api import sync_playwright

    url = "https://www.tc.gob.pe/jurisprudencia/"
    output_file = "data/nuevas_sentencias_tc.json"
    os.makedirs("data", exist_ok=True)
    
    print(f"\n1. Iniciando navegador visible...")
    with sync_playwright() as p:
        # Abrimos en modo headed (visible) para que puedas resolver CAPTCHAs si aparecen
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"2. Navegando al portal: {url}")
        page.goto(url)
        
        print("\n[INSTRUCCIONES DE USO]")
        print("-----------------------------------------------------------------")
        print("1. En la ventana del navegador que se ha abierto, realiza la búsqueda")
        print("   de tu interés (ej. busca 'desnaturalizacion de contrato' o 'Ley 24041').")
        print("2. Una vez que se muestren los resultados en pantalla, presiona ENTER")
        print("   en esta consola para que el script proceda a extraer los datos.")
        print("-----------------------------------------------------------------")
        
        input("\nPresiona ENTER cuando los resultados de la búsqueda estén cargados en el navegador...")
        
        print("\n3. Extrayendo contenido de la página actual...")
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Este selector es referencial y debe adaptarse a la estructura HTML exacta del buscador del TC
        # Por lo general, las sentencias se listan en tablas o listas de enlaces.
        resultados = []
        
        # Ejemplo de extracción buscando enlaces a resoluciones (.pdf o .html)
        enlaces_sentencias = soup.find_all('a', href=re.compile(r'/jurisprudencia/\d{4}/'))
        
        print(f"Se encontraron {len(enlaces_sentencias)} posibles resoluciones en pantalla.")
        
        for idx, link in enumerate(enlaces_sentencias):
            titulo = link.text.strip()
            href = link.get('href')
            full_url = href if href.startswith('http') else f"https://www.tc.gob.pe{href}"
            
            # Buscar texto o sumilla descriptiva cercana (hermano o ancestro común)
            parent = link.find_parent()
            resumen = ""
            if parent:
                resumen = parent.text.strip()
            
            # Limpieza básica
            resumen_limpio = re.sub(r'\s+', ' ', resumen)
            
            resultados.append({
                "ID": f"SCRAP_TC_{int(time.time())}_{idx}",
                "titulo": titulo if titulo else f"Resolucion TC - {idx}",
                "abstract": resumen_limpio[:500], # Guardamos un fragmento del texto circundante
                "url_pdf": full_url,
                "categoria": "Poder Judicial / TC",
                "fecha": datetime.date.today().strftime("%d/%m/%Y") if 'datetime' in globals() else "18/07/2026",
                "metadata_pretension": "Desnaturalizacion de Contrato"
            })
            
        if resultados:
            # Guardar datos extraídos
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Datos guardados con éxito en {output_file} ({len(resultados)} registros).")
            print("Puedes incorporar estos datos a tu Parquet principal ejecutando un script de unión.")
        else:
            print("\n❌ No se lograron extraer registros. Verifica la estructura del HTML e intenta adaptando los selectores en el script.")
            
        browser.close()

if __name__ == "__main__":
    main()
