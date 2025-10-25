"""
Script para generar datos sintéticos de mortalidad para Colombia 2019
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Configurar semilla para reproducibilidad
np.random.seed(42)
random.seed(42)

# Departamentos de Colombia
DEPARTAMENTOS = {
    '05': 'ANTIOQUIA', '08': 'ATLANTICO', '11': 'BOGOTA', '13': 'BOLIVAR',
    '15': 'BOYACA', '17': 'CALDAS', '19': 'CAUCA', '23': 'CORDOBA',
    '25': 'CUNDINAMARCA', '27': 'CHOCO', '41': 'HUILA', '44': 'LA GUAJIRA',
    '47': 'MAGDALENA', '50': 'META', '52': 'NARIÑO', '54': 'N. SANTANDER',
    '63': 'QUINDIO', '66': 'RISARALDA', '68': 'SANTANDER', '70': 'SUCRE',
    '73': 'TOLIMA', '76': 'VALLE', '81': 'ARAUCA', '85': 'CASANARE',
    '86': 'PUTUMAYO', '91': 'AMAZONAS', '94': 'GUAINIA', '95': 'GUAVIARE',
    '97': 'VAUPES', '99': 'VICHADA'
}

# Municipios principales por departamento
MUNICIPIOS = {
    '05': ['05001', '05002', '05004', '05021', '05030'],  # Medellín, etc
    '08': ['08001', '08078', '08137', '08141', '08296'],  # Barranquilla, etc
    '11': ['11001'],  # Bogotá
    '76': ['76001', '76020', '76036', '76109', '76111'],  # Cali, etc
}

# Causas de muerte (CIE-10)
CAUSAS = [
    ('I21', 'INFARTO AGUDO DEL MIOCARDIO'),
    ('I64', 'ACCIDENTE CEREBROVASCULAR'),
    ('J18', 'NEUMONIA'),
    ('E14', 'DIABETES MELLITUS'),
    ('C34', 'TUMOR MALIGNO DE LOS BRONQUIOS Y DEL PULMON'),
    ('X95', 'AGRESION CON ARMA DE FUEGO'),
    ('V89', 'ACCIDENTE DE VEHICULO DE MOTOR'),
    ('J44', 'ENFERMEDAD PULMONAR OBSTRUCTIVA CRONICA'),
    ('K70', 'ENFERMEDAD ALCOHOLICA DEL HIGADO'),
    ('I25', 'CARDIOPATIA ISQUEMICA CRONICA'),
]

# Grupos de edad
GRUPOS_EDAD = [
    ('0', 'Menores de 1 mes', 0, 0),
    ('1', '1-11 meses', 0, 1),
    ('7', '1-4 años', 1, 4),
    ('9', '5-14 años', 5, 14),
    ('11', '15-19 años', 15, 19),
    ('12', '20-24 años', 20, 24),
    ('13', '25-29 años', 25, 29),
    ('14', '30-34 años', 30, 34),
    ('15', '35-39 años', 35, 39),
    ('16', '40-44 años', 40, 44),
    ('17', '45-49 años', 45, 49),
    ('18', '50-54 años', 50, 54),
    ('19', '55-59 años', 55, 59),
    ('20', '60-64 años', 60, 64),
    ('21', '65-69 años', 65, 69),
    ('22', '70-74 años', 70, 74),
    ('23', '75-79 años', 75, 79),
    ('24', '80-84 años', 80, 84),
    ('25', '85+ años', 85, 100),
]

def generate_deaths(n_records=50000):
    """Generar datos sintéticos de muertes"""
    records = []
    
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 12, 31)
    
    for i in range(n_records):
        # Fecha aleatoria en 2019
        days = random.randint(0, 364)
        fecha = start_date + timedelta(days=days)
        mes = fecha.month
        
        # Departamento y municipio
        cod_dpto = random.choice(list(DEPARTAMENTOS.keys()))
        if cod_dpto in MUNICIPIOS:
            cod_mun = random.choice(MUNICIPIOS[cod_dpto])
        else:
            cod_mun = f"{cod_dpto}001"
        
        # Sexo (más muertes masculinas en general)
        sexo = random.choices(['Masculino', 'Femenino'], weights=[55, 45])[0]
        
        # Grupo de edad (más muertes en mayores)
        grupo_edad = random.choices(
            GRUPOS_EDAD,
            weights=[2, 3, 5, 8, 10, 12, 15, 18, 20, 22, 25, 30, 35, 40, 50, 60, 70, 80, 90]
        )[0]
        
        edad = random.randint(grupo_edad[2], grupo_edad[3])
        
        # Causa de muerte
        causa = random.choice(CAUSAS)
        
        # Manera de muerte
        if causa[0] == 'X95':
            manera = 'Homicidio'
        elif causa[0].startswith('V'):
            manera = 'Accidente'
        else:
            manera = 'Natural'
        
        record = {
            'AÑO': 2019,
            'MES': mes,
            'COD_DEPARTAMENTO': cod_dpto,
            'DEPARTAMENTO': DEPARTAMENTOS[cod_dpto],
            'COD_MUNICIPIO': cod_mun,
            'MUNICIPIO': f'MUNICIPIO_{cod_mun}',
            'SEXO': sexo,
            'EDAD': edad,
            'GRUPO_EDAD1': grupo_edad[0],
            'GRUPO_EDAD_DESC': grupo_edad[1],
            'COD_MUERTE': causa[0],
            'CAUSA_MUERTE': causa[1],
            'MANERA_MUERTE': manera,
        }
        
        records.append(record)
    
    return pd.DataFrame(records)

def generate_causas():
    """Generar tabla de causas"""
    causas_extendidas = CAUSAS + [
        ('I50', 'INSUFICIENCIA CARDIACA'),
        ('N18', 'ENFERMEDAD RENAL CRONICA'),
        ('C50', 'TUMOR MALIGNO DE LA MAMA'),
        ('C16', 'TUMOR MALIGNO DEL ESTOMAGO'),
        ('K74', 'FIBROSIS Y CIRROSIS DEL HIGADO'),
        ('J81', 'EDEMA PULMONAR'),
        ('I69', 'SECUELAS DE ENFERMEDAD CEREBROVASCULAR'),
        ('Y34', 'EVENTOS DE INTENCION NO DETERMINADA'),
        ('X47', 'ENVENENAMIENTO ACCIDENTAL'),
        ('W19', 'CAIDA NO ESPECIFICADA'),
    ]
    
    return pd.DataFrame(causas_extendidas, columns=['COD_MUERTE', 'NOMBRE'])

def generate_divipola():
    """Generar tabla DIVIPOLA"""
    records = []
    
    for cod_dpto, nombre_dpto in DEPARTAMENTOS.items():
        if cod_dpto in MUNICIPIOS:
            for cod_mun in MUNICIPIOS[cod_dpto]:
                records.append({
                    'COD_DEPARTAMENTO': cod_dpto,
                    'DEPARTAMENTO': nombre_dpto,
                    'COD_MUNICIPIO': cod_mun,
                    'MUNICIPIO': f'MUNICIPIO_{cod_mun}'
                })
        else:
            # Al menos un municipio por departamento
            records.append({
                'COD_DEPARTAMENTO': cod_dpto,
                'DEPARTAMENTO': nombre_dpto,
                'COD_MUNICIPIO': f'{cod_dpto}001',
                'MUNICIPIO': f'MUNICIPIO_{cod_dpto}001'
            })
    
    return pd.DataFrame(records)

if __name__ == '__main__':
    import os
    from sqlalchemy import create_engine
    
    # Obtener URL de la base de datos
    db_url = os.getenv('DB_URL', 'mysql+mysqlconnector://mortalidad_user:mortalidad_pass@db:3306/mortalidad_db')
    
    print("🔄 Generando datos sintéticos...")
    
    # Generar datos
    df_muertes = generate_deaths(50000)
    df_causas = generate_causas()
    df_divipola = generate_divipola()
    
    print(f"✅ Generados {len(df_muertes)} registros de muertes")
    print(f"✅ Generados {len(df_causas)} causas de muerte")
    print(f"✅ Generados {len(df_divipola)} registros DIVIPOLA")
    
    # Conectar a la base de datos
    print(f"\n🔄 Conectando a la base de datos...")
    engine = create_engine(db_url)
    
    # Cargar datos
    print("🔄 Cargando datos en la base de datos...")
    
    df_causas.to_sql('causas', engine, if_exists='replace', index=False)
    print("✅ Tabla 'causas' cargada")
    
    df_divipola.to_sql('divipola', engine, if_exists='replace', index=False)
    print("✅ Tabla 'divipola' cargada")
    
    df_muertes.to_sql('muertes', engine, if_exists='replace', index=False, chunksize=1000)
    print("✅ Tabla 'muertes' cargada")
    
    print("\n🎉 ¡Datos cargados exitosamente!")
    print(f"\nResumen:")
    print(f"  - Muertes: {len(df_muertes):,} registros")
    print(f"  - Causas: {len(df_causas)} registros")
    print(f"  - DIVIPOLA: {len(df_divipola)} registros")
