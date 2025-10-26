"""
Script para cargar datos sintéticos en la base de datos MySQL
Compatible con el esquema de muertes existente
"""
import mysql.connector
import random
from datetime import datetime, timedelta

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'mortalidad_user',
    'password': 'mortalidad_pass',
    'database': 'mortalidad_db'
}

# Departamentos de Colombia
DEPARTAMENTOS = [
    'ANTIOQUIA', 'ATLANTICO', 'BOGOTA', 'BOLIVAR', 'BOYACA',
    'CALDAS', 'CAUCA', 'CORDOBA', 'CUNDINAMARCA', 'CHOCO',
    'HUILA', 'LA GUAJIRA', 'MAGDALENA', 'META', 'NARIÑO',
    'N. SANTANDER', 'QUINDIO', 'RISARALDA', 'SANTANDER', 'SUCRE',
    'TOLIMA', 'VALLE', 'ARAUCA', 'CASANARE', 'PUTUMAYO',
    'AMAZONAS', 'GUAINIA', 'GUAVIARE', 'VAUPES', 'VICHADA'
]

# Causas de muerte (CIE-10)
CAUSAS_CIE10 = [
    ('I21', 'INFARTO AGUDO DEL MIOCARDIO'),
    ('I64', 'ACCIDENTE CEREBROVASCULAR'),
    ('J18', 'NEUMONIA'),
    ('E14', 'DIABETES MELLITUS'),
    ('C34', 'TUMOR MALIGNO DE PULMON'),
    ('X95', 'AGRESION CON ARMA DE FUEGO'),
    ('V89', 'ACCIDENTE DE VEHICULO'),
    ('J44', 'EPOC'),
    ('K70', 'ENFERMEDAD HEPATICA'),
    ('I25', 'CARDIOPATIA ISQUEMICA'),
    ('I50', 'INSUFICIENCIA CARDIACA'),
    ('N18', 'ENFERMEDAD RENAL'),
    ('C50', 'TUMOR MALIGNO DE MAMA'),
    ('Y09', 'AGRESION'),
    ('X93', 'AGRESION CON ARMA BLANCA'),
    ('Y04', 'AGRESION FISICA'),
    ('J81', 'EDEMA PULMONAR'),
    ('I69', 'SECUELAS CEREBROVASCULARES'),
    ('X47', 'ENVENENAMIENTO'),
    ('W19', 'CAIDA'),
]

# Grupos de edad
GRUPOS_EDAD = [
    ('0-17', 0, 17),
    ('18-29', 18, 29),
    ('30-44', 30, 44),
    ('45-59', 45, 59),
    ('60+', 60, 95),
]

def connect_db():
    """Conectar a la base de datos"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✅ Conexión exitosa a la base de datos")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error de conexión: {err}")
        return None

def insert_causas(cursor):
    """Insertar causas en la tabla causas"""
    print("\n📋 Insertando causas...")
    
    for codigo, descripcion in CAUSAS_CIE10:
        try:
            cursor.execute(
                "INSERT IGNORE INTO causas (codigo, descripcion) VALUES (%s, %s)",
                (codigo, descripcion)
            )
        except mysql.connector.Error as err:
            print(f"⚠️ Error insertando causa {codigo}: {err}")
    
    print(f"✅ {len(CAUSAS_CIE10)} causas insertadas")

def insert_divipola(cursor):
    """Insertar datos DIVIPOLA"""
    print("\n🗺️ Insertando datos DIVIPOLA...")
    
    municipios_por_depto = ['MUNICIPIO_' + str(i) for i in range(1, 6)]
    
    for depto in DEPARTAMENTOS:
        for mun in municipios_por_depto:
            codigo = f"{DEPARTAMENTOS.index(depto):02d}{municipios_por_depto.index(mun):03d}"
            try:
                cursor.execute(
                    "INSERT INTO divipola (departamento, municipio, codigo_divipola) VALUES (%s, %s, %s)",
                    (depto, mun, codigo)
                )
            except mysql.connector.Error as err:
                print(f"⚠️ Error insertando DIVIPOLA: {err}")
                break
        break  # Solo insertar para 1 departamento por ahora
    
    print("✅ Datos DIVIPOLA insertados")

def insert_muertes(cursor, n_records=50000):
    """Insertar registros de muertes"""
    print(f"\n💀 Generando {n_records} registros de muertes...")
    
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 12, 31)
    
    batch_size = 1000
    records = []
    
    for i in range(n_records):
        # Fecha aleatoria en 2019
        days = random.randint(0, 364)
        fecha = (start_date + timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Departamento y municipio
        departamento = random.choice(DEPARTAMENTOS)
        municipio = f'MUNICIPIO_{random.randint(1, 50)}'
        
        # Sexo (M o F)
        sexo = random.choices(['M', 'F'], weights=[55, 45])[0]
        
        # Grupo de edad
        grupo = random.choices(
            GRUPOS_EDAD,
            weights=[5, 15, 25, 30, 25]
        )[0]
        
        edad = random.randint(grupo[1], grupo[2])
        grupo_edad = grupo[0]
        
        # Causa de muerte
        causa = random.choice(CAUSAS_CIE10)[0]
        
        records.append((fecha, departamento, municipio, sexo, edad, grupo_edad, causa))
        
        # Insertar en lotes
        if len(records) >= batch_size:
            try:
                cursor.executemany(
                    """INSERT INTO muertes 
                       (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    records
                )
                print(f"  ✓ Insertados {i+1}/{n_records} registros...")
                records = []
            except mysql.connector.Error as err:
                print(f"❌ Error insertando lote: {err}")
                records = []
    
    # Insertar registros restantes
    if records:
        try:
            cursor.executemany(
                """INSERT INTO muertes 
                   (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                records
            )
        except mysql.connector.Error as err:
            print(f"❌ Error insertando último lote: {err}")
    
    print(f"✅ {n_records} registros de muertes insertados")

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 CARGA DE DATOS SINTÉTICOS - DASHBOARD DE MORTALIDAD")
    print("=" * 60)
    
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # Insertar causas
        insert_causas(cursor)
        conn.commit()
        
        # Insertar DIVIPOLA
        insert_divipola(cursor)
        conn.commit()
        
        # Insertar muertes
        insert_muertes(cursor, n_records=50000)
        conn.commit()
        
        # Verificar registros
        cursor.execute("SELECT COUNT(*) FROM muertes")
        total = cursor.fetchone()[0]
        
        print("\n" + "=" * 60)
        print(f"✅ CARGA COMPLETADA - Total de muertes: {total:,}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
