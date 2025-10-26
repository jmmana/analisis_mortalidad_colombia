"""
Script para preparar datos geográficos de Colombia
Descarga y prepara GeoJSON de departamentos y municipios
"""
import requests
import json
import os

def download_colombia_geojson():
    """Descarga geometrías de Colombia desde datos abiertos"""
    
    # URL de datos abiertos de Colombia (DANE)
    # Usando una fuente alternativa con datos simplificados
    departamentos_url = "https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json"
    
    output_dir = "data/geodata"
    os.makedirs(output_dir, exist_ok=True)
    
    print("📥 Descargando geometrías de departamentos de Colombia...")
    
    try:
        response = requests.get(departamentos_url, timeout=30)
        response.raise_for_status()
        
        geojson_data = response.json()
        
        # Guardar el archivo
        output_path = os.path.join(output_dir, "colombia_departamentos.geojson")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Archivo guardado en: {output_path}")
        print(f"📊 Departamentos encontrados: {len(geojson_data.get('features', []))}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error descargando datos: {e}")
        print("💡 Creando archivo de ejemplo...")
        create_sample_geojson(output_dir)
        return None

def create_sample_geojson(output_dir):
    """Crea un GeoJSON de ejemplo con algunos departamentos"""
    sample_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "DPTO": "11",
                    "NOMBRE_DPT": "BOGOTA D.C."
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-74.2, 4.5], [-74.0, 4.5], [-74.0, 4.7], [-74.2, 4.7], [-74.2, 4.5]
                    ]]
                }
            }
        ]
    }
    
    output_path = os.path.join(output_dir, "colombia_departamentos.geojson")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Archivo de ejemplo creado: {output_path}")

if __name__ == "__main__":
    download_colombia_geojson()
