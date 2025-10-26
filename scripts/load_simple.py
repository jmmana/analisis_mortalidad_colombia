"""
Script SIMPLIFICADO para cargar datos reales
"""
import pandas as pd
import mysql.connector

# Configuración
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'mortalidad_user',
    'password': 'mortalidad_pass',
    'database': 'mortalidad_db'
}

print("Conectando...")
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()
print("✅ Conectado")

# 1. CARGAR DIVIPOLA
print("\n🗺️ Cargando DIVIPOLA...")
df_div = pd.read_excel("D:\\Codigos\\Dashboard de Mortalidad\\data\\Divipola_CE_.xlsx")
print(f"Columnas: {list(df_div.columns)}")

for _, row in df_div.iterrows():
    try:
        cursor.execute(
            "INSERT IGNORE INTO divipola (departamento, municipio, codigo_divipola) VALUES (%s, %s, %s)",
            (str(row['DEPARTAMENTO']), str(row['MUNICIPIO']), str(row['COD_DANE']))
        )
    except:
        pass

conn.commit()
cursor.execute("SELECT COUNT(*) FROM divipola")
print(f"✅ {cursor.fetchone()[0]} registros DIVIPOLA")

# 2. CARGAR CAUSAS - intentar diferentes sheets
print("\n📋 Cargando causas...")
try:
    # Intentar sheet 0
    df_causas = pd.read_excel("D:\\Codigos\\Dashboard de Mortalidad\\data\\Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx", sheet_name=0, skiprows=3)
    print(f"Columnas encontradas: {list(df_causas.columns)}")
    
    # Si tiene columnas con nombres, usar las primeras 2
    if len(df_causas.columns) >= 2:
        col_codigo = df_causas.columns[0]
        col_desc = df_causas.columns[1]
        
        for _, row in df_causas.iterrows():
            try:
                codigo = str(row[col_codigo])[:10]
                desc = str(row[col_desc])[:255]
                if codigo and codigo != 'nan' and desc and desc != 'nan':
                    cursor.execute(
                        "INSERT IGNORE INTO causas (codigo, descripcion) VALUES (%s, %s)",
                        (codigo, desc)
                    )
            except:
                pass
                
        conn.commit()
except Exception as e:
    print(f"⚠️ Error causas: {e}")

cursor.execute("SELECT COUNT(*) FROM causas")
print(f"✅ {cursor.fetchone()[0]} causas")

# 3. CARGAR MUERTES
print("\n💀 Cargando muertes (esto puede tardar varios minutos)...")
print("Leyendo archivo Excel completo...")

try:
    # Leer todo el archivo
    df_muertes = pd.read_excel("D:\\Codigos\\Dashboard de Mortalidad\\data\\Anexo1.NoFetal2019_CE_15-03-23.xlsx")
    
    print(f"✓ Archivo cargado: {len(df_muertes):,} registros")
    print(f"  Columnas: {list(df_muertes.columns)[:15]}...")  # Mostrar solo primeras 15
    
    records = []
    total_inserted = 0
    batch_size = 1000
    
    for idx, row in df_muertes.iterrows():
        try:
            # Extraer campos comunes
            fecha = '2019-01-01'  # Default
            if 'ANO' in df_muertes.columns:
                ano = row['ANO'] if pd.notna(row['ANO']) else 2019
                mes = row['MES'] if 'MES' in df_muertes.columns and pd.notna(row['MES']) else 1
                dia = 1
                fecha = f"{int(ano):04d}-{int(mes):02d}-{dia:02d}"
            
            # Buscar departamento
            depto = 'DESCONOCIDO'
            for col in ['DEPARTAMENTO', 'DEPTO', 'COD_DEPARTAMENTO']:
                if col in df_muertes.columns and pd.notna(row[col]):
                    depto = str(row[col])[:100]
                    break
            
            # Buscar municipio
            muni = 'DESCONOCIDO'
            for col in ['MUNICIPIO', 'MUNI', 'COD_MUNICIPIO']:
                if col in df_muertes.columns and pd.notna(row[col]):
                    muni = str(row[col])[:100]
                    break
            
            # Sexo
            sexo = 'M'
            if 'SEXO' in df_muertes.columns and pd.notna(row['SEXO']):
                sexo_val = str(row['SEXO']).upper()
                sexo = sexo_val[0] if sexo_val else 'M'
            
            # Edad
            edad = 0
            for col in ['EDAD', 'EDAD_ANOS']:
                if col in df_muertes.columns and pd.notna(row[col]):
                    try:
                        edad = int(float(row[col]))
                    except:
                        edad = 0
                    break
            
            # Grupo edad
            if edad < 18:
                grupo_edad = '0-17'
            elif edad < 30:
                grupo_edad = '18-29'
            elif edad < 45:
                grupo_edad = '30-44'
            elif edad < 60:
                grupo_edad = '45-59'
            else:
                grupo_edad = '60+'
            
            # Causa
            causa = 'XXX'
            for col in ['CAUSA', 'COD_CAUSA', 'CAUSABAS', 'CIE10']:
                if col in df_muertes.columns and pd.notna(row[col]):
                    causa = str(row[col])[:10]
                    break
            
            records.append((fecha, depto, muni, sexo, edad, grupo_edad, causa))
            
            # Insertar en lotes
            if len(records) >= batch_size:
                cursor.executemany(
                    "INSERT INTO muertes (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    records
                )
                conn.commit()
                total_inserted += len(records)
                print(f"  ✓ Procesados {idx+1:,}/{len(df_muertes):,} (Insertados: {total_inserted:,})")
                records = []
            
        except Exception as e:
            continue
    
    # Insertar registros restantes
    if records:
        cursor.executemany(
            "INSERT INTO muertes (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            records
        )
        conn.commit()
        total_inserted += len(records)
    
    print(f"\n✅ Total muertes insertadas: {total_inserted:,}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Resumen final
print("\n" + "="*60)
cursor.execute("SELECT COUNT(*) FROM divipola")
print(f"DIVIPOLA: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM causas")
print(f"CAUSAS: {cursor.fetchone()[0]:,}")

cursor.execute("SELECT COUNT(*) FROM muertes")
print(f"MUERTES: {cursor.fetchone()[0]:,}")
print("="*60)

cursor.close()
conn.close()
print("\n✅ COMPLETADO")
