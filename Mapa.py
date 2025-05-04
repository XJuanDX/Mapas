import streamlit as st
import csv
import os
import requests
from urllib.parse import urlparse, parse_qs

# ---------- Funciones ----------

def extraer_coordenadas(enlace):
    try:
        parsed_url = urlparse(enlace)
        if "@" in parsed_url.path:
            coords = parsed_url.path.split("@")[1].split(",")
            if len(coords) >= 2:
                return float(coords[0]), float(coords[1])
        query = parse_qs(parsed_url.query)
        if "q" in query:
            q_val = query["q"][0]
            if "," in q_val:
                lat, lon = q_val.split(",")
                return float(lat), float(lon)
    except:
        pass
    return None, None

def registrar_cliente(nombre, lat, lon):
    with open("clientes.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nombre, lat, lon])

def cargar_clientes():
    if not os.path.exists("clientes.csv"):
        with open("clientes.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre", "Latitud", "Longitud"])
    with open("clientes.csv", mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        return list(reader)

# ---------- Interfaz ----------

st.title("Registro de Clientes y Optimización de Ruta")

tab1, tab2, tab3 = st.tabs(["Registrar Manual", "Registrar por Enlace", "Optimizar Ruta"])

with tab1:
    st.header("Registro Manual")
    nombre = st.text_input("Nombre")
    lat = st.text_input("Latitud")
    lon = st.text_input("Longitud")
    if st.button("Registrar Cliente Manualmente"):
        try:
            registrar_cliente(nombre, float(lat), float(lon))
            st.success("Cliente registrado.")
        except:
            st.error("Latitud y longitud inválidas.")

with tab2:
    st.header("Registro por Enlace de Google Maps")
    nombre2 = st.text_input("Nombre del Cliente")
    enlace = st.text_input("Enlace de Google Maps")
    if st.button("Registrar desde Enlace"):
        lat, lon = extraer_coordenadas(enlace)
        if lat is not None:
            registrar_cliente(nombre2, lat, lon)
            st.success("Cliente registrado con coordenadas.")
        else:
            st.error("No se pudieron extraer coordenadas.")

with tab3:
    st.header("Optimizar Ruta")
    clientes = cargar_clientes()
    opciones = [f"{c[0]} ({c[1]}, {c[2]})" for c in clientes]
    
    inicio = st.selectbox("Punto de inicio", opciones)
    fin = st.selectbox("Punto final", opciones)
    paradas = st.multiselect("Paradas intermedias", opciones)

    if st.button("Calcular Ruta"):
        def obtener_coords(cliente_str):
            nombre = cliente_str.split(" (")[0]
            for c in clientes:
                if c[0] == nombre:
                    return f"{c[1]},{c[2]}"
            return ""

        origin = obtener_coords(inicio)
        destination = obtener_coords(fin)
        waypoints = [obtener_coords(p) for p in paradas]

        key = "AIzaSyD-HxXkhbhuFrfpNbmmVL80hMgFMv66pVI" 
        url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={'|'.join(waypoints)}"

        st.markdown(f"[Abrir ruta optimizada en Google Maps](url)", unsafe_allow_html=False)
