import streamlit as st
import csv
import os
import requests
import webbrowser
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
# Función para calcular la ruta
def calcular_ruta():
    inicio = combobox_inicio.get()
    fin = combobox_fin.get()
    if not inicio or not fin:
        messagebox.showwarning("Advertencia", "Seleccione un punto de inicio y fin.")
        return
    
    paradas_seleccionadas = []
    with open('clientes.csv', mode='r', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        next(lector)
        clientes = list(lector)
    
    for i, var in enumerate(check_vars):
        if var.get() == 1:
            paradas_seleccionadas.append(f"{clientes[i][0]} ({clientes[i][1]}, {clientes[i][2]})")
    
    inicio_coords = fin_coords = None
    paradas_coords = []
    for cliente in clientes:
        nombre_cliente = f"{cliente[0]} ({cliente[1]}, {cliente[2]})"
        if nombre_cliente == inicio:
            inicio_coords = f"{cliente[1]},{cliente[2]}"
        if nombre_cliente == fin:
            fin_coords = f"{cliente[1]},{cliente[2]}"
        if nombre_cliente in paradas_seleccionadas:
            paradas_coords.append(f"{cliente[1]},{cliente[2]}")
    
    if not inicio_coords or not fin_coords:
        messagebox.showerror("Error", "No se encontraron coordenadas de inicio o fin.")
        return
    
    api_key = "AIzaSyD-HxXkhbhuFrfpNbmmVL80hMgFMv66pVI"  # Reemplaza con tu API key
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={inicio_coords}&destination={fin_coords}&waypoints=optimize:true|{'|'.join(paradas_coords)}&key={api_key}"
    respuesta = requests.get(url).json()
    
    if respuesta['status'] == 'OK':
        ruta = respuesta['routes'][0]
        orden_paradas = ruta['waypoint_order']
        paradas_ordenadas = [paradas_coords[i] for i in orden_paradas]
        
        lista_orden.delete(0, tk.END)
        lista_orden.insert(tk.END, "Orden de paradas optimizado:")
        for i, p in enumerate(orden_paradas):
            lista_orden.insert(tk.END, f"{i+1}. {paradas_seleccionadas[p]}")
        
        enlace_maps = f"https://www.google.com/maps/dir/?api=1&origin={inicio_coords}&destination={fin_coords}&waypoints={'|'.join(paradas_ordenadas)}"
        webbrowser.open(enlace_maps)
    else:
        messagebox.showerror("Error", "No se pudo calcular la ruta.")
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

        st.markdown(f"[Abrir ruta optimizada en Google Maps]({url})", unsafe_allow_html=False)
