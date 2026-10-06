import pandas as pd

# 1. lee el CSV crudo (Bronze)
df = pd.read_csv("data/bronze/telemetria.csv")
filas_leidas = len(df)
print(f"Filas leidas: {filas_leidas}")

# --- regla 1: duplicados exactos ---
duplicados = df.duplicated()
n_duplicados = duplicados.sum()
df = df[~duplicados]  # nos quedamos solo con las filas que NO son duplicado
print(f"Rechazadas por duplicado: {n_duplicados}")

# --- regla 2: datos faltantes (irradiancia vacía) ---
faltantes = df["irradiancia_wm2"].isna()
n_faltantes = faltantes.sum()
df = df[~faltantes]
print(f"Rechazadas por dato faltante: {n_faltantes}")

# --- regla 3: rango físico válido ---
# Un inversor de 5 kWp no debería reportar potencia negativa ni irradiancia fuera de 0-1200 W/m2
rango_invalido = (df["p_ac_kw"] < 0) | (df["irradiancia_wm2"] < 0) | (df["irradiancia_wm2"] > 1200)
n_rango_invalido = rango_invalido.sum()
df = df[~rango_invalido]
print(f"Rechazadas por rango fisico inválido: {n_rango_invalido}")

# --- resumen final ---
filas_validas = len(df)
pct_validas = round(100 * filas_validas / filas_leidas, 2)
print(f"Filas válidas: {filas_validas}")
print(f"Porcentaje de datos válidos: {pct_validas}%")

# guarda el resultado limpio en Silver
df.to_csv("data/silver/lecturas_5min_limpias.csv", index=False)
print("Archivo guardado en data/silver/lecturas_5min_limpias.csv")