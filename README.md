# Proyecto sobre el veto en el Consejo de Seguridad de las Naciones Unidas

Dashboard interactivo que analiza el uso del derecho de veto por parte de los cinco miembros permanentes del Consejo de Seguridad de la ONU (URSS/Rusia, EE. UU., Reino Unido, Francia y China) desde 1946 hasta la actualidad.

## 🚀 Demo en vivo
Puedes explorar la aplicación funcionando aquí: **[veto-onu.onrender.com](https://veto-onu.onrender.com)**

## 📊 Características principales
El dashboard está dividido en cuatro pestañas interactivas:
*   **📊 Resumen:** Visualización global de los vetos por década y por país, incluyendo un gráfico de dona y un análisis de los temas más vetados (Medio Oriente, Admisión de miembros, etc.).
*   **🎬 Evolución:** Animación interactiva año por año (1946-hoy) que muestra cómo ha crecido el uso del veto por parte de cada país a lo largo de la historia.
*   **⚔️ Compara:** Herramienta cara a cara para contrastar la actividad de dos países, incluyendo el año de su primer veto.
*   **🎯 Desafío:** Un minijuego de trivia de 5 preguntas con pistas y puntuación, calculado dinámicamente con los datos reales de la app.

## 🛠️ Tecnologías utilizadas
*   **Python** (Lenguaje principal)
*   **Streamlit** (Framework de la interfaz web)
*   **Pandas** (Procesamiento y limpieza de datos)
*   **Plotly** (Gráficos interactivos y animaciones)
*   **BeautifulSoup4 & Requests** (Web scraping para la extracción de datos)

## 📂 Origen de los datos
Los datos no son simulados. Fueron extraídos directamente de la lista oficial de vetos de la **Biblioteca Dag Hammarskjöld de la ONU**.
*   `vetos.csv`: Datos agregados por década y país (usados por la app).
*   `vetos_detalle.csv`: Registro histórico uno a uno (año, país y tema del veto).
*   `obtener_datos.py`: Script de Python que automatiza la descarga y limpieza de los datos desde la página de la ONU.

## ⚙️ Cómo ejecutar este proyecto en local
Si quieres correrlo en tu computadora:
1. Clona el repositorio: `git clone https://github.com/diegoglez122/Proyecto-sobre-el-veto-en-el-Consejo-de-Seguridad-de-las-Naciones-Unidas.git`
2. Crea un entorno virtual: `python3 -m venv .venv`
3. Actívalo: `source .venv/bin/activate` (en Linux/Mac) o `.venv\Scripts\activate` (en Windows).
4. Instala las dependencias: `pip install -r requirements.txt`
5. Ejecuta la app: `streamlit run app.py`

---
*Nota: Este proyecto fue desplegado en Render para garantizar su accesibilidad global.*
