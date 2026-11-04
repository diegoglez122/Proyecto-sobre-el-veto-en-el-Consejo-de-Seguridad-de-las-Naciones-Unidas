"""Descarga la lista oficial de vetos (Biblioteca Dag Hammarskjöld, ONU)
y genera vetos_detalle.csv (un registro por veto) y vetos.csv (para la app).

Uso:  pip install requests beautifulsoup4 pandas
      python obtener_datos.py
"""
import re
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://www.un.org/Depts/dhl/resguide/scact_veto_table_en.htm"

PAISES = [  # (patrón en la celda del miembro, nombre en la app)
    (r"USSR|Russia", "URSS/Rusia"),
    (r"\bUSA\b|\bUS\b|United States", "EE. UU."),
    (r"\bUK\b|United Kingdom", "Reino Unido"),
    (r"France", "Francia"),
    (r"China", "China"),
]

TEMAS = [  # (patrón en el punto de agenda, tema); el orden importa
    (r"Membership|Admission", "Admisión de miembros"),
    (r"Non-proliferation|Democratic People", "No proliferación / Corea del Norte"),
    (r"Ukrain", "Ucrania"),
    (r"Palestin|Arab territories|Middle East|Syria", "Medio Oriente"),
    (r"Namibia|South Africa|Rhodesia|Angola|Southern Africa", "África austral"),
]


def tema(texto):
    for pat, nombre in TEMAS:
        if re.search(pat, texto, re.I):
            return nombre
    return "Otros"


def parsear(html):
    soup = BeautifulSoup(html, "html.parser")
    filas = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        fecha = tds[0].get_text(" ", strip=True)
        anio = re.search(r"(1[9]\d\d|20\d\d)", fecha)
        if not anio:
            continue  # cabecera u otra fila
        agenda = tds[-2].get_text(" ", strip=True)
        miembros = tds[-1].get_text(" ", strip=True)
        for pat, nombre in PAISES:
            if re.search(pat, miembros):
                filas.append({"fecha": fecha, "anio": int(anio.group(1)),
                              "pais": nombre, "punto_agenda": agenda,
                              "tema": tema(agenda)})
    return pd.DataFrame(filas)


def main():
    r = requests.get(URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    df = parsear(r.text)
    if df.empty:
        sys.exit("No se encontraron filas: revisa la estructura de la página.")
    df["decada"] = (df["anio"] // 10 * 10).astype(str) + "s"
    df.to_csv("vetos_detalle.csv", index=False)
    agg = df.groupby(["decada", "pais"]).size().rename("vetos").reset_index()
    agg.to_csv("vetos.csv", index=False)
    print(df.groupby("pais").size().sort_values(ascending=False))
    print("Total:", len(df), "| años", df.anio.min(), "-", df.anio.max())


if __name__ == "__main__":
    main()
