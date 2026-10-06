import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

BRONZE = "data/bronze/telemetria.csv"
SILVER = "data/silver/lecturas_5min_limpias.csv"


def limpiar(df):
    """Aplica las 3 reglas de calidad y reporta cuántas filas rechaza cada una."""
    print(f"Filas leídas: {len(df)}")

    dup = df.duplicated()
    print(f"Rechazadas por duplicado: {int(dup.sum())}")
    df = df[~dup]

    falt = df["irradiancia_wm2"].isna()
    print(f"Rechazadas por dato faltante: {int(falt.sum())}")
    df = df[~falt]

    rango = (df["p_ac_kw"] < 0) | (df["irradiancia_wm2"] < 0) | (df["irradiancia_wm2"] > 1200)
    print(f"Rechazadas por rango físico inválido: {int(rango.sum())}")
    return df[~rango]


def main():
    # 1. Bronze -> Silver
    raw = pd.read_csv(BRONZE)
    raw["fecha"] = pd.to_datetime(raw["ts"]).dt.date
    limpio = limpiar(raw).copy()
    pct_total = round(100 * len(limpio) / len(raw), 2)
    print(f"Filas válidas: {len(limpio)}")
    print(f"Porcentaje de datos válidos: {pct_total}%")

    limpio.drop(columns="fecha").to_csv(SILVER, index=False)

    # 2. Resumen diario (energía = potencia * 5/60 h)
    limpio["energia_kwh"] = limpio["p_ac_kw"] * 5 / 60
    leidas_dia = raw.groupby(["fecha", "dispositivo_id"]).size().rename("leidas")
    resumen = (
        limpio.groupby(["fecha", "dispositivo_id"])
        .agg(energia_kwh=("energia_kwh", "sum"), validas=("ts", "count"))
        .join(leidas_dia)
        .reset_index()
    )
    resumen["energia_kwh"] = resumen["energia_kwh"].round(3)
    resumen["pct_datos_validos"] = (100 * resumen["validas"] / resumen["leidas"]).round(2)

    # 3. Cargar a PostgreSQL con UPSERT (idempotente)
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "solarbi"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD"),
    )
    with conn, conn.cursor() as cur:
        lecturas = limpio[["ts", "dispositivo_id", "p_ac_kw", "irradiancia_wm2", "temp_modulo_c"]]
        filas = list(lecturas.astype(object).itertuples(index=False, name=None))
        execute_values(cur, """
            INSERT INTO silver.lectura_5min
                (ts, dispositivo_id, p_ac_kw, irradiancia_wm2, temp_modulo_c)
            VALUES %s
            ON CONFLICT (ts, dispositivo_id) DO UPDATE SET
                p_ac_kw = EXCLUDED.p_ac_kw,
                irradiancia_wm2 = EXCLUDED.irradiancia_wm2,
                temp_modulo_c = EXCLUDED.temp_modulo_c
        """, filas)

        diario = resumen[["fecha", "dispositivo_id", "energia_kwh", "pct_datos_validos"]]
        filas = list(diario.astype(object).itertuples(index=False, name=None))
        execute_values(cur, """
            INSERT INTO dwh.fact_energia_dia
                (fecha, dispositivo_id, energia_kwh, pct_datos_validos)
            VALUES %s
            ON CONFLICT (fecha, dispositivo_id) DO UPDATE SET
                energia_kwh = EXCLUDED.energia_kwh,
                pct_datos_validos = EXCLUDED.pct_datos_validos
        """, filas)

        cur.execute("SELECT COUNT(*) FROM silver.lectura_5min")
        print(f"silver.lectura_5min: {cur.fetchone()[0]} filas")
        cur.execute("SELECT COUNT(*) FROM dwh.fact_energia_dia")
        print(f"dwh.fact_energia_dia: {cur.fetchone()[0]} filas")
    conn.close()


if __name__ == "__main__":
    main()