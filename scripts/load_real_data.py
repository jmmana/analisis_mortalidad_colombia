"""
Script para cargar datos REALES desde archivos Excel a la base de datos MySQL
"""
import pandas as pd
import mysql.connector
from datetime import datetime
import sys

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'mortalidad_user',
    'password': 'mortalidad_pass',
    'database': 'mortalidad_db'
}

def connect_db():
    """Conectar a la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Conexión exitosa a la base de datos")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error de conexión: {err}")
        return None

def load_divipola(filepath, cursor):
    """Cargar datos DIVIPOLA desde Excel"""
    print(f"\n🗺️ Cargando DIVIPOLA desde {filepath}...")
    
    try:
        df = pd.read_excel(filepath)
        print(f"  Columnas encontradas: {list(df.columns)}")
        
        # Mostrar primeras filas para entender estructura
        print("\n  Primeras 3 filas:")
        print(df.head(3))
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                # Ajustar según las columnas reales del archivo
                departamento = str(row.iloc[0]) if len(row) > 0 else None
                municipio = str(row.iloc[1]) if len(row) > 1 else None
                codigo = str(row.iloc[2]) if len(row) > 2 else None
                
                if departamento and departamento != 'nan':
                    cursor.execute(
                        "INSERT IGNORE INTO divipola (departamento, municipio, codigo_divipola) VALUES (%s, %s, %s)",
                        (departamento, municipio, codigo)
                    )
                    records_inserted += 1
            except Exception as e:
                print(f"  ⚠️ Error en fila: {e}")
                continue
        
        print(f"✅ {records_inserted} registros DIVIPOLA insertados")
        return True
        
    except Exception as e:
        print(f"❌ Error cargando DIVIPOLA: {e}")
        return False

def load_causas(filepath, cursor):
    """Cargar códigos de muerte desde Excel"""
    print(f"\n📋 Cargando causas de muerte desde {filepath}...")
    
    try:
        df = pd.read_excel(filepath)
        print(f"  Columnas encontradas: {list(df.columns)}")
        print(f"  Total de filas: {len(df)}")
        
        # Mostrar primeras filas
        print("\n  Primeras 3 filas:")
        print(df.head(3))
        
        records_inserted = 0
        for _, row in df.iterrows():
            try:
                # Ajustar según columnas reales
                codigo = str(row.iloc[0]) if len(row) > 0 else None
                descripcion = str(row.iloc[1]) if len(row) > 1 else None
                
                if codigo and codigo != 'nan' and descripcion and descripcion != 'nan':
                    cursor.execute(
                        "INSERT IGNORE INTO causas (codigo, descripcion) VALUES (%s, %s)",
                        (codigo[:10], descripcion[:255])  # Limitar longitud
                    )
                    records_inserted += 1
            except Exception as e:
                print(f"  ⚠️ Error en fila: {e}")
                continue
        
        print(f"✅ {records_inserted} causas insertadas")
        return True
        
    except Exception as e:
        print(f"❌ Error cargando causas: {e}")
        return False

def load_muertes(filepath, cursor, batch_size=1000):
    """Cargar datos de muertes no fetales desde Excel"""
    print(f"\n💀 Cargando muertes desde {filepath}...")
    
    try:
        # Leer Excel
        print("  Leyendo archivo Excel (puede tardar)...")
        df = pd.read_excel(filepath)
        
        print(f"  Columnas encontradas: {list(df.columns)}")
        print(f"  Total de registros: {len(df):,}")
        
        # Mostrar primeras filas
        print("\n  Primeras 3 filas:")
        print(df.head(3))
        
        # Preparar datos
        records = []
        errors = 0
        
        for idx, row in df.iterrows():
            try:
                # Extraer campos (ajustar según columnas reales)
                # Asumiendo columnas típicas de certificados de defunción
                
                # Fecha - buscar columnas de fecha
                fecha = None
                for col in df.columns:
                    if 'fecha' in col.lower() or 'ano' in col.lower():
                        fecha_val = row[col]
                        if pd.notna(fecha_val):
                            if isinstance(fecha_val, datetime):
                                fecha = fecha_val.strftime('%Y-%m-%d')
                            elif isinstance(fecha_val, str):
                                fecha = fecha_val
                            else:
                                fecha = '2019-01-01'  # Default
                            break
                
                if not fecha:
                    fecha = '2019-01-01'
                
                # Departamento y municipio
                departamento = None
                municipio = None
                for col in df.columns:
                    if 'depart' in col.lower():
                        departamento = str(row[col]) if pd.notna(row[col]) else 'DESCONOCIDO'
                    if 'munic' in col.lower() and not municipio:
                        municipio = str(row[col]) if pd.notna(row[col]) else 'DESCONOCIDO'
                
                if not departamento:
                    departamento = 'DESCONOCIDO'
                if not municipio:
                    municipio = 'DESCONOCIDO'
                
                # Sexo
                sexo = 'M'  # Default
                for col in df.columns:
                    if 'sexo' in col.lower():
                        sexo_val = str(row[col]).upper() if pd.notna(row[col]) else 'M'
                        sexo = sexo_val[0] if sexo_val else 'M'
                        break
                
                # Edad
                edad = 0
                for col in df.columns:
                    if 'edad' in col.lower():
                        edad_val = row[col]
                        if pd.notna(edad_val):
                            try:
                                edad = int(float(edad_val))
                            except:
                                edad = 0
                        break
                
                # Grupo de edad
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
                
                # Causa de muerte (código CIE-10)
                codigo_causa = None
                for col in df.columns:
                    if 'causa' in col.lower() or 'cie' in col.lower():
                        causa_val = row[col]
                        if pd.notna(causa_val):
                            codigo_causa = str(causa_val)[:10]
                            break
                
                if not codigo_causa:
                    codigo_causa = 'XXX'  # Código desconocido
                
                # Agregar registro
                records.append((
                    fecha,
                    departamento[:100],
                    municipio[:100],
                    sexo[:1],
                    edad,
                    grupo_edad[:50],
                    codigo_causa[:10]
                ))
                
                # Insertar en lotes
                if len(records) >= batch_size:
                    cursor.executemany(
                        """INSERT INTO muertes 
                           (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        records
                    )
                    print(f"  ✓ Procesados {idx+1:,}/{len(df):,} registros...")
                    records = []
                    
            except Exception as e:
                errors += 1
                if errors < 10:  # Mostrar solo primeros 10 errores
                    print(f"  ⚠️ Error en fila {idx}: {e}")
                continue
        
        # Insertar registros restantes
        if records:
            cursor.executemany(
                """INSERT INTO muertes 
                   (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                records
            )
        
        print(f"✅ Carga completada. Errores: {errors}")
        return True
        
    except Exception as e:
        print(f"❌ Error cargando muertes: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("=" * 80)
    print("🚀 CARGA DE DATOS REALES - DASHBOARD DE MORTALIDAD COLOMBIA 2019")
    print("=" * 80)
    
    # Rutas de archivos
    base_path = "D:\\Codigos\\Dashboard de Mortalidad\\data\\"
    divipola_file = base_path + "Divipola_CE_.xlsx"
    causas_file = base_path + "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"
    muertes_file = base_path + "Anexo1.NoFetal2019_CE_15-03-23.xlsx"
    
    # Conectar a BD
    conn = connect_db()
    if not conn:
        sys.exit(1)
    
    cursor = conn.cursor()
    
    try:
        # 1. Cargar DIVIPOLA
        if load_divipola(divipola_file, cursor):
            conn.commit()
        
        # 2. Cargar Causas
        if load_causas(causas_file, cursor):
            conn.commit()
        
        # 3. Cargar Muertes
        if load_muertes(muertes_file, cursor):
            conn.commit()
        
        # Verificar resultados
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE CARGA:")
        print("=" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM divipola")
        print(f"  DIVIPOLA: {cursor.fetchone()[0]:,} registros")
        
        cursor.execute("SELECT COUNT(*) FROM causas")
        print(f"  CAUSAS: {cursor.fetchone()[0]:,} registros")
        
        cursor.execute("SELECT COUNT(*) FROM muertes")
        total_muertes = cursor.fetchone()[0]
        print(f"  MUERTES: {total_muertes:,} registros")
        
        print("\n✅ CARGA COMPLETADA EXITOSAMENTE!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
