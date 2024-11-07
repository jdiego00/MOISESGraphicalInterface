"""Imports data"""

import pandas


def handler(source: str) -> pandas.DataFrame:
    df = pandas.read_csv(source)

    df['Año'] = pandas.to_datetime(df['Año'], format='%Y')

    # Convertir unidades de energía (kbep a gigajulios, 1 kbep = 41.868 GJ)
    df['Cantidad_GJ'] = df['Cantidad'] * 41.868
    return df
