"""
Generar datos sintéticos basados en la estructura real de DIVIPOLA
"""
import mysql.connector
import random
from datetime import datetime, timedelta

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

# Obtener departamentos y municipios reales de DIVIPOLA
print("\n📍 Obteniendo datos de DIVIPOLA...")
cursor.execute("SELECT DISTINCT departamento FROM divipola WHERE departamento IS NOT NULL")
departamentos = [row[0] for row in cursor.fetchall() if row[0] and row[0] != 'nan']

cursor.execute("SELECT departamento, municipio FROM divipola WHERE municipio IS NOT NULL LIMIT 100")
municipios = [(row[0], row[1]) for row in cursor.fetchall() if row[0] and row[1]]

print(f"✓ {len(departamentos)} departamentos")
print(f"✓ {len(municipios)} municipios")

# Obtener causas reales
cursor.execute("SELECT codigo FROM causas")
causas = [row[0] for row in cursor.fetchall()]
print(f"✓ {len(causas)} causas")

if not causas:
    # Insertar causas básicas si no hay
    causas_basicas = [
        ('I21', 'INFARTO'), ('I64', 'ACV'), ('J18', 'NEUMONIA'),
        ('E14', 'DIABETES'), ('C34', 'CANCER'), ('X95', 'HOMICIDIO'),
        ('V89', 'ACCIDENTE'), ('J44', 'EPOC'), ('K70', 'HEPATICA'),
        ('I25', 'ISQUEMICA')
    ]
    for cod, desc in causas_basicas:
        cursor.execute("INSERT IGNORE INTO causas (codigo, descripcion) VALUES (%s, %s)", (cod, desc))
    conn.commit()
    causas = [c[0] for c in causas_basicas]

# Generar 50,000 registros de muertes
print(f"\n💀 Generando 50,000 registros...")
records = []
start_date = datetime(2019, 1, 1)

for i in range(50000):
    days = random.randint(0, 364)
    fecha = (start_date + timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Usar departamento y municipio reales
    if municipios:
        depto, muni = random.choice(municipios)
    else:
        depto = random.choice(departamentos) if departamentos else 'BOGOTA'
        muni = 'MUNICIPIO_1'
    
    sexo = random.choice(['M', 'F'])
    edad = random.randint(0, 95)
    
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
    
    causa = random.choice(causas)
    
    records.append((fecha, depto, muni, sexo, edad, grupo_edad, causa))
    
    if len(records) >= 1000:
        cursor.executemany(
            "INSERT INTO muertes (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            records
        )
        conn.commit()
        print(f"  ✓ {i+1:,}/50,000")
        records = []

if records:
    cursor.executemany(
        "INSERT INTO muertes (fecha, departamento, municipio, sexo, edad, grupo_edad, codigo_causa) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        records
    )
    conn.commit()

# Verificar
cursor.execute("SELECT COUNT(*) FROM muertes")
total = cursor.fetchone()[0]

print(f"\n{'='*60}")
print(f"✅ COMPLETADO: {total:,} muertes registradas")
print(f"{'='*60}")

cursor.close()
conn.close()
