"""
===============================================================================
PROYECTO: TanqueLleno AI — Fase M (Modelado)
ARCHIVO:  scripts/obtener_macro.py
DESCRIPCIÓN:
    Ingesta de las variables macroeconómicas líderes que la Fase R declaró en
    semáforo ROJO: crudo WTI, crudo Brent y tipo de cambio S//US$.

    Ambas fuentes son públicas y no requieren clave de API:
      - FRED (Federal Reserve Bank of St. Louis) para WTI y Brent.
      - BCRP (Banco Central de Reserva del Perú) para el tipo de cambio.

    El archivo se guarda con el valor del **mes cerrado**. El rezago a t-1 que
    exige el protocolo anti-leakage NO se aplica aquí: lo aplica
    `features._adjuntar_macro()` al unir con el panel. Mantener el rezago en un
    solo lugar evita el error de aplicarlo dos veces o ninguna.

USO:
    python scripts/obtener_macro.py
    python scripts/obtener_macro.py --desde 2019-01-01
===============================================================================
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import urllib.error
import urllib.request

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from tanquelleno import config

TIEMPO_ESPERA_S = 30

SERIES_FRED = {
    "wti": "DCOILWTICO",      # WTI spot, Cushing, US$ por barril
    "brent": "DCOILBRENTEU",  # Brent spot, US$ por barril
}
# Tipo de cambio bancario promedio del periodo, venta (S/ por US$).
SERIE_BCRP = "PN01207PM"

ERRORES_DE_RED = (urllib.error.URLError, OSError, ValueError, KeyError, IndexError)


def _descargar(url: str) -> str:
    peticion = urllib.request.Request(url, headers={"User-Agent": "tanquelleno-ai/1.0"})
    with urllib.request.urlopen(peticion, timeout=TIEMPO_ESPERA_S) as respuesta:
        return respuesta.read().decode("utf-8", errors="replace")


def descargar_fred(id_serie: str, nombre: str) -> pd.DataFrame:
    """Descarga una serie diaria de FRED y la agrega a promedio mensual."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={id_serie}"
    df = pd.read_csv(io.StringIO(_descargar(url)))

    col_fecha, col_valor = df.columns[0], df.columns[1]
    df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
    df[col_valor] = pd.to_numeric(df[col_valor], errors="coerce")
    df = df.dropna(subset=[col_fecha, col_valor])

    return (
        df.set_index(col_fecha)[col_valor]
        .resample("MS")
        .mean()
        .rename(nombre)
        .reset_index()
        .rename(columns={col_fecha: "ym"})
    )


def descargar_bcrp(id_serie: str = SERIE_BCRP, nombre: str = "tipo_cambio") -> pd.DataFrame:
    """Descarga una serie mensual del BCRP."""
    url = (
        f"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/"
        f"{id_serie}/csv/2019-1/2030-12"
    )
    df = pd.read_csv(io.StringIO(_descargar(url)), skiprows=1, names=["periodo", nombre])
    df[nombre] = pd.to_numeric(
        df[nombre].astype(str).str.replace(",", "."), errors="coerce"
    )

    meses = {
        "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12,
    }

    def _a_fecha(periodo: str) -> pd.Timestamp | None:
        partes = str(periodo).strip().split(".")
        if len(partes) != 2 or partes[0] not in meses:
            return None
        anio = int(partes[1])
        anio += 2000 if anio < 100 else 0
        return pd.Timestamp(year=anio, month=meses[partes[0]], day=1)

    df["ym"] = df["periodo"].map(_a_fecha)
    return df.dropna(subset=["ym", nombre])[["ym", nombre]]


def main(desde: str = "2019-01-01") -> pd.DataFrame:
    print("=" * 78)
    print("INGESTA DE VARIABLES MACROECONÓMICAS LÍDERES")
    print("=" * 78)

    marcos, errores = [], []

    for nombre, id_serie in SERIES_FRED.items():
        try:
            df = descargar_fred(id_serie, nombre)
            marcos.append(df)
            print(f"  [OK]    {nombre:12s} FRED/{id_serie:14s} {len(df):4d} meses "
                  f"({df['ym'].min().date()} -> {df['ym'].max().date()})")
        except ERRORES_DE_RED as exc:
            errores.append(f"{nombre} (FRED/{id_serie}): {exc}")
            print(f"  [FALLO] {nombre:12s} FRED/{id_serie:14s} {exc}")

    try:
        df = descargar_bcrp()
        marcos.append(df)
        print(f"  [OK]    {'tipo_cambio':12s} BCRP/{SERIE_BCRP:14s} {len(df):4d} meses "
              f"({df['ym'].min().date()} -> {df['ym'].max().date()})")
    except ERRORES_DE_RED as exc:
        errores.append(f"tipo_cambio (BCRP/{SERIE_BCRP}): {exc}")
        print(f"  [FALLO] {'tipo_cambio':12s} BCRP/{SERIE_BCRP:14s} {exc}")

    if not marcos:
        # Sin ninguna serie no se escribe un archivo vacío: `features` detecta
        # su ausencia y entrena sin macro, declarándolo en el reporte. Escribir
        # un CSV con columnas nulas haría creer que la ingesta sí funcionó.
        print("\nNo se pudo descargar ninguna serie. No se escribe archivo.")
        print("El entrenamiento continuará sin variables macro y lo declarará "
              "en reportes/metricas_a2.json.")
        for err in errores:
            print(f"  - {err}")
        raise SystemExit(1)

    macro = marcos[0]
    for df in marcos[1:]:
        macro = macro.merge(df, on="ym", how="outer")

    macro = macro[macro["ym"] >= pd.Timestamp(desde)].sort_values("ym").reset_index(drop=True)

    # El crack spread de la Costa del Golfo no está disponible sin suscripción;
    # se aproxima por la diferencia Brent-WTI, que es un proxy del diferencial
    # de refinación y se declara como tal, no como el margen real.
    if {"brent", "wti"} <= set(macro.columns):
        macro["spread_brent_wti"] = macro["brent"] - macro["wti"]

    os.makedirs(config.DATOS_DIR, exist_ok=True)
    macro.to_csv(config.F_MACRO, index=False)

    print(f"\n  Filas: {len(macro)} | Columnas: {[c for c in macro.columns if c != 'ym']}")
    print(f"  Guardado: {os.path.relpath(config.F_MACRO, config.PROJECT_ROOT)}")
    if errores:
        print(f"\n  Series no obtenidas ({len(errores)}):")
        for err in errores:
            print(f"    - {err}")
    print("\n  Siguiente paso: python modelado/entrenamiento_a2.py")
    print("=" * 78)
    return macro


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga las variables macro líderes.")
    parser.add_argument("--desde", default="2019-01-01",
                        help="Fecha mínima a conservar (YYYY-MM-DD).")
    args = parser.parse_args()
    main(args.desde)
