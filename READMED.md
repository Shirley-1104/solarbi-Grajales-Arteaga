\# SolarBI Pascual — Consulta BI Grupo 50



\*\*Integrantes:\*\* Shirley Grajales, Sammy Arteaga

\*\*Curso / Grupo:\*\* Inteligencia de Negocios · Grupo 50

\*\*Docente:\*\* Ramiro Grisales Montoya



\## Descripción

Trabajo de consulta sobre Power BI vs. Grafana, gobernanza de datos, automatización ETL e IoT, aplicado al proyecto SolarBI Pascual. Incluye una práctica guiada que simula telemetría de un inversor solar, la limpia con reglas de calidad, la carga en PostgreSQL, y la visualiza en Power BI y en Grafana.



\## Estructura del repositorio

\- `docs/` — PDF de la consulta (entrega final)

\- `data/bronze/` — datos crudos simulados (no se modifican)

\- `data/silver/` — datos limpios, después de aplicar reglas de calidad

\- `etl/` — `simulador.py` (genera Bronze) y `run\_etl.py` (limpia y carga a PostgreSQL)

\- `sql/` — scripts de creación de tablas y cargas en PostgreSQL

\- `powerbi/` — archivo `.pbix` o proyecto `.pbip`

\- `grafana/` — `dashboard.json` exportado



\## Cómo reproducir la práctica

1\. `python etl/simulador.py` — genera `data/bronze/telemetria.csv`

2\. `python etl/run\_etl.py` — limpia los datos, los carga en PostgreSQL y genera el resumen diario

3\. Abrir `powerbi/` en Power BI Desktop y conectar a PostgreSQL

4\. Importar `grafana/dashboard.json` en una instancia local de Grafana





