# Análisis de Mortalidad — Colombia 📊

Repositorio: https://github.com/jmmana/analisis_mortalidad_colombia.git

Breve: Proyecto para procesar, analizar y visualizar datos de mortalidad en Colombia usando Python, Dash/Plotly y MySQL. Contiene ETL, dashboard interactivo y artefactos para contenerización y despliegue.

---

## Badges

[![license-MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![build](https://img.shields.io/badge/build-pending-lightgrey)](https://github.com/jmmana/analisis_mortalidad_colombia/actions)

---

## Quick start (Windows - PowerShell)

1. Clonar el repositorio:

```powershell
git clone https://github.com/jmmana/analisis_mortalidad_colombia.git
cd analisis_mortalidad_colombia
```

2. Crear y activar entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Configurar variables de entorno:

```text
# Crear archivo .env en la raíz con las variables mínimas
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mortalidad_db
DB_USER=mortalidad_user
DB_PASS=mortalidad_pass
APP_PORT=8050
```

5. (Dev) Levantar servicios con Docker Compose:

```powershell
docker compose up --build -d
```

6. Ejecutar ETL (ejemplo):

```powershell
python etl/load_data.py --data-dir data --db-url "mysql+mysqlconnector://mortalidad_user:mortalidad_pass@localhost:3306/mortalidad_db"
```

7. Ejecutar la app:

```powershell
python app.py
# o con gunicorn para producción
gunicorn "app:app" -b 0.0.0.0:8050 --workers 4
```

---

## Estructura del repositorio

```
.
├── README.md
├── Guía Implementacion.md   # Guía técnica y plan de implementación (estado y pasos)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── data/                    # Datos (no versionar datos sensibles)
├── etl/                     # Scripts ETL
├── src/                     # Código de la app (dashboard, db, queries)
├── tests/                   # Pruebas automatizadas
└── config/                  # SQL y configs
```

---

## Estado y seguimiento

El tablero de estado principal está en `Guía Implementacion.md` (sección "📌 Estado del proyecto — Seguimiento"). Actualiza las casillas allí cuando avances.

---

## Contribuir

1. Haz fork y crea una rama: `git checkout -b feat/tu-cambio`.
2. Añade tests y documentación para tus cambios.
3. Abre un Pull Request describiendo los cambios y cómo probarlos.

Lee `Guía Implementacion.md` para la guía de estilo y el proceso recomendado.

---

## Licencia

Este proyecto usa la licencia MIT (añadir `LICENSE` si aplica).

---

<img width="608" height="338" alt="image" src="https://github.com/user-attachments/assets/6db351bb-0428-47bf-be69-03d74afa8f7b" />
<img width="622" height="344" alt="image" src="https://github.com/user-attachments/assets/449b08af-152e-4605-b106-1b99ed897da9" />
<img width="631" height="340" alt="image" src="https://github.com/user-attachments/assets/12497c5f-a692-4876-8021-f2d34c34ae45" />



