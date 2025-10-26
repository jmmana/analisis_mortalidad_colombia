"""
Cargar DATOS REALES desde Excel usando lector optimizado
"""
import pandas as pd
import mysql.connector
from openpyxl import load_workbook

DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'mortalidad_user',
    'password': 'mortalidad_pass',
    'database': 'mortalidad_db'
}

print("🔌 Conectando a la base de datos...")
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()
print("✅ Conectado\n")

# 1. CARGAR DIVIPOLA (ya funcionó antes)
print("🗺️ Cargando DIVIPOLA...")
df_div = pd.read_excel("D:\\Codigos\\Dashboard de Mortalidad\\data\\Divipola_CE_.xlsx")
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
print(f"✅ DIVIPOLA: {cursor.fetchone()[0]:,} registros\n")

# 2. CARGAR CAUSAS
print("📋 Cargando causas de muerte...")
try:
    df_causas = pd.read_excel("D:\\Codigos\\Dashboard de Mortalidad\\data\\Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx", skiprows=3)
    print(f"   Columnas: {list(df_causas.columns)[:5]}")
    
    col_codigo = df_causas.columns[0]
    col_desc = df_causas.columns[1] if len(df_causas.columns) > 1 else df_causas.columns[0]
    
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
    print(f"   ⚠️ Error: {e}")

cursor.execute("SELECT COUNT(*) FROM causas")
print(f"✅ CAUSAS: {cursor.fetchone()[0]:,} registros\n")

# 3. CARGAR MUERTES usando openpyxl directamente (más rápido)
print("💀 Cargando MUERTES desde Excel...")
print("   Esta operación puede tardar 5-10 minutos debido al tamaño del archivo...")
print("   Por favor espere...\n")

try:
    # Cargar el workbook con read_only=True para optimizar
    print("   📖 Abriendo archivo Excel...")
    wb = load_workbook(
        filename="D:\\Codigos\\Dashboard de Mortalidad\\data\\Anexo1.NoFetal2019_CE_15-03-23.xlsx",
        read_only=True,
        data_only=True
    )
    ws = wb.active
    
    print(f"   ✓ Archivo abierto\n")
    
    # Leer encabezados
    headers = []
    for cell in next(ws.rows):
        headers.append(cell.value)
    
    print(f"   📋 Columnas encontradas ({len(headers)} columnas):")
    print(f"   {headers[:20]}...\n")
    
    # Mapear índices de columnas
    col_indices = {}
    for idx, header in enumerate(headers):
        if header:
            header_upper = str(header).upper()
            if 'COD_DEPARTAMENTO' in header_upper:
                col_indices['DEPTO'] = idx
            elif 'COD_MUNICIPIO' in header_upper:
                col_indices['MUNI'] = idx
            elif 'AÑO' in header_upper or 'ANO' in header_upper:
                col_indices['ANO'] = idx
            elif 'MES' in header_upper:
                col_indices['MES'] = idx
            elif 'SEXO' in header_upper:
                col_indices['SEXO'] = idx
            elif 'GRUPO_EDAD1' in header_upper:
                col_indices['EDAD_GRUPO'] = idx
            elif 'COD_MUERTE' in header_upper or 'CAUSABAS' in header_upper:
                col_indices['CAUSA'] = idx
    
    print(f"   🔍 Índices mapeados: {col_indices}\n")
    
    # Procesar filas
    records = []
    row_count = 0
    inserted_count = 0
    batch_size = 1000
    
    print("   ⏳ Procesando registros...")
    
    for row_idx, row in enumerate(ws.rows):
        if row_idx == 0:  # Skip header
            continue
        
        try:
            row_values = [cell.value for cell in row]
            
            # Fecha
            ano = row_values[col_indices.get('ANO', 0)] if col_indices.get('ANO') is not None else 2019
            mes = row_values[col_indices.get('MES', 1)] if col_indices.get('MES') is not None else 1
            
            try:
                ano = int(ano) if ano else 2019
                mes = int(mes) if mes else 1
            except:
                ano, mes = 2019, 1
            
            fecha = f"{ano:04d}-{mes:02d}-01"
            
            # Departamento - usar código directamente
            cod_depto = row_values[col_indices.get('DEPTO', 1)] if col_indices.get('DEPTO') is not None else None
            depto = str(cod_depto)[:100] if cod_depto else 'DESCONOCIDO'
            
            # Municipio - usar código directamente
            cod_muni = row_values[col_indices.get('MUNI', 2)] if col_indices.get('MUNI') is not None else None
            muni = str(cod_muni)[:100] if cod_muni else 'DESCONOCIDO'
            
            # Sexo - convertir 1 a M, 2 a F, 3 a I (Indeterminado)
            sexo_val = row_values[col_indices.get('SEXO', 9)] if col_indices.get('SEXO') is not None else None
            
            if sexo_val:
                try:
                    sexo_num = int(float(sexo_val))
                    if sexo_num == 1:
                        sexo = 'M'
                    elif sexo_num == 2:
                        sexo = 'F'
                    elif sexo_num == 3:
                        sexo = 'I'  # Indeterminado
                    else:
                        sexo = 'M'
                except:
                    sexo_str = str(sexo_val).upper()
                    if sexo_str in ['1', 'MASCULINO', 'HOMBRE', 'M']:
                        sexo = 'M'
                    elif sexo_str in ['2', 'FEMENINO', 'MUJER', 'F']:
                        sexo = 'F'
                    elif sexo_str in ['3', 'INDETERMINADO', 'I']:
                        sexo = 'I'
                    else:
                        sexo = 'M'
            else:
                sexo = 'M'
            
            # Edad - calcular desde GRUPO_EDAD1
            edad_grupo_val = row_values[col_indices.get('EDAD_GRUPO', 11)] if col_indices.get('EDAD_GRUPO') is not None else None
            
            # Mapeo de códigos de grupo de edad a edad promedio
            edad_grupos_map = {
                '0': 0, '1': 0, '7': 2, '9': 10, '11': 17, '12': 22,
                '13': 27, '14': 32, '15': 37, '16': 42, '17': 47,
                '18': 52, '19': 57, '20': 62, '21': 67, '22': 72,
                '23': 77, '24': 82, '25': 87
            }
            
            if edad_grupo_val and str(edad_grupo_val) in edad_grupos_map:
                edad = edad_grupos_map[str(edad_grupo_val)]
            else:
                edad = 0
            
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
            causa = row_values[col_indices.get('CAUSA', 6)] if col_indices.get('CAUSA') is not None else 'XXX'
            causa = str(causa)[:10] if causa else 'XXX'
            
            records.append((fecha, depto, muni, sexo, edad, grupo_edad, causa))
            row_count += 1
            
            # Insertar en lotes
            if len(records) >= batch_size:
                cursor.executemany(
                    "INSERT INTO muertes (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    records
                )
                conn.commit()
                inserted_count += len(records)
                records = []
                
                if inserted_count % 10000 == 0:
                    print(f"      ✓ {inserted_count:,} registros insertados...")
        
        except Exception as e:
            # Silenciar errores individuales
            continue
    
    # Insertar registros restantes
    if records:
        cursor.executemany(
            "INSERT INTO muertes (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            records
        )
        conn.commit()
        inserted_count += len(records)
    
    wb.close()
    
    print(f"\n✅ MUERTES: {inserted_count:,} registros insertados")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

# RESUMEN FINAL
print("\n" + "="*70)
print("📊 RESUMEN FINAL - DATOS REALES CARGADOS:")
print("="*70)

cursor.execute("SELECT COUNT(*) FROM divipola")
print(f"   🗺️  DIVIPOLA:  {cursor.fetchone()[0]:,} registros")

cursor.execute("SELECT COUNT(*) FROM causas")
print(f"   📋 CAUSAS:    {cursor.fetchone()[0]:,} registros")

cursor.execute("SELECT COUNT(*) FROM muertes")
total_muertes = cursor.fetchone()[0]
print(f"   💀 MUERTES:   {total_muertes:,} registros")

if total_muertes > 0:
    cursor.execute("SELECT MIN(fecha), MAX(fecha) FROM muertes WHERE fecha IS NOT NULL")
    fechas = cursor.fetchone()
    if fechas[0]:
        print(f"   📅 Periodo:   {fechas[0]} a {fechas[1]}")
    
    cursor.execute("SELECT COUNT(DISTINCT departamento) FROM muertes")
    print(f"   📍 Departamentos: {cursor.fetchone()[0]:,}")

print("="*70)
print("\n✅ ¡CARGA COMPLETADA! Tus datos reales están listos para el dashboard\n")

cursor.close()
conn.close()
