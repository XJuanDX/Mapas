import csv
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
from urllib.parse import urlparse, parse_qs
from ttkthemes import ThemedTk

# Función para extraer coordenadas de un enlace de Google Maps
def extraer_coordenadas(enlace):
    try:
        parsed_url = urlparse(enlace)
        if "@" in parsed_url.path:
            coordenadas = parsed_url.path.split("@")[1].split(",")
            if len(coordenadas) >= 2:
                return float(coordenadas[0]), float(coordenadas[1])
        query_params = parse_qs(parsed_url.query)
        if "q" in query_params:
            q_value = query_params["q"][0]
            if "," in q_value:
                lat, lon = q_value.split(",")
                return float(lat), float(lon)
        return None, None
    except Exception as e:
        print(f"Error al extraer coordenadas: {e}")
        return None, None

# Función para registrar cliente manualmente
def registrar_cliente_manual():
    nombre = entry_nombre.get()
    latitud = entry_latitud.get()
    longitud = entry_longitud.get()
    if nombre and latitud and longitud:
        try:
            latitud = float(latitud)
            longitud = float(longitud)
            with open('clientes.csv', mode='a', newline='', encoding='utf-8') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow([nombre, latitud, longitud])
            messagebox.showinfo("Éxito", "Cliente registrado con éxito.")
            limpiar_campos()
            actualizar_listas()
        except ValueError:
            messagebox.showerror("Error", "Latitud y longitud deben ser números válidos.")
            entry_latitud.configure(style="Error.TEntry")
            entry_longitud.configure(style="Error.TEntry")
    else:
        messagebox.showwarning("Advertencia", "Complete todos los campos.")
        if not nombre: entry_nombre.configure(style="Error.TEntry")
        if not latitud: entry_latitud.configure(style="Error.TEntry")
        if not longitud: entry_longitud.configure(style="Error.TEntry")

# Función para registrar cliente por enlace
def registrar_cliente_enlace():
    nombre = entry_nombre.get()
    enlace = entry_enlace.get()
    if nombre and enlace:
        latitud, longitud = extraer_coordenadas(enlace)
        if latitud is not None and longitud is not None:
            with open('clientes.csv', mode='a', newline='', encoding='utf-8') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow([nombre, latitud, longitud])
            messagebox.showinfo("Éxito", "Cliente registrado con éxito.")
            limpiar_campos()
            actualizar_listas()
        else:
            messagebox.showerror("Error", "No se pudieron extraer coordenadas del enlace.")
            entry_enlace.configure(style="Error.TEntry")
    else:
        messagebox.showwarning("Advertencia", "Complete todos los campos.")
        if not nombre: entry_nombre.configure(style="Error.TEntry")
        if not enlace: entry_enlace.configure(style="Error.TEntry")

# Función para limpiar campos
def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_latitud.delete(0, tk.END)
    entry_longitud.delete(0, tk.END)
    entry_enlace.delete(0, tk.END)
    entry_nombre.configure(style="TEntry")
    entry_latitud.configure(style="TEntry")
    entry_longitud.configure(style="TEntry")
    entry_enlace.configure(style="TEntry")

# Función para actualizar listas y checkboxes
def actualizar_listas():
    with open('clientes.csv', mode='r', encoding='utf-8') as archivo:
        lector = csv.reader(archivo)
        next(lector)  # Saltar encabezados
        clientes = list(lector)
    
    nombres_clientes = [f"{c[0]} ({c[1]}, {c[2]})" for c in clientes]
    combobox_inicio['values'] = nombres_clientes
    combobox_fin['values'] = nombres_clientes
    
    for widget in frame_paradas.winfo_children():
        widget.destroy()
    
    global check_vars
    check_vars = []
    for i, cliente in enumerate(nombres_clientes):
        var = tk.IntVar()
        check_vars.append(var)
        checkbox = ttk.Checkbutton(frame_paradas, text=cliente, variable=var)
        checkbox.grid(row=i, column=0, sticky="w")

# Función para desplazarse con la rueda del mouse
def _on_mousewheel(event):
    canvas_paradas.yview_scroll(-1 * (event.delta // 120), "units")

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

# Crear ventana principal con tema
ventana = ThemedTk(theme="arc")
ventana.title("Registro de Clientes y Optimización de Ruta")
ventana.geometry("800x600")
ventana.resizable(True, True)

# Configurar estilo para campos con error
style = ttk.Style()
style.configure("Error.TEntry", fieldbackground="#ffcccc")
style.configure("Accent.TButton", background="#4CAF50", foreground="white")

# Frame para registro
frame_registro = ttk.LabelFrame(ventana, text="Registro de Clientes", padding=10)
frame_registro.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

notebook = ttk.Notebook(frame_registro)
notebook.pack(fill="both", expand=True)

# Pestaña manual
frame_manual = ttk.Frame(notebook)
notebook.add(frame_manual, text="Registro Manual")

tk.Label(frame_manual, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
entry_nombre = ttk.Entry(frame_manual, width=30)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_manual, text="Latitud:").grid(row=1, column=0, padx=5, pady=5)
entry_latitud = ttk.Entry(frame_manual, width=30)
entry_latitud.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_manual, text="Longitud:").grid(row=2, column=0, padx=5, pady=5)
entry_longitud = ttk.Entry(frame_manual, width=30)
entry_longitud.grid(row=2, column=1, padx=5, pady=5)

ttk.Button(frame_manual, text="Registrar", command=registrar_cliente_manual).grid(row=3, column=0, columnspan=2, pady=5)

# Pestaña enlace
frame_enlace = ttk.Frame(notebook)
notebook.add(frame_enlace, text="Registro por Enlace")

tk.Label(frame_enlace, text="Enlace:").grid(row=0, column=0, padx=5, pady=5)
entry_enlace = ttk.Entry(frame_enlace, width=30)
entry_enlace.grid(row=0, column=1, padx=5, pady=5)

ttk.Button(frame_enlace, text="Registrar", command=registrar_cliente_enlace).grid(row=1, column=0, columnspan=2, pady=5)

# Frame para selección de ruta
frame_ruta = ttk.LabelFrame(ventana, text="Configuración de Ruta", padding=10)
frame_ruta.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

tk.Label(frame_ruta, text="Inicio:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
combobox_inicio = ttk.Combobox(frame_ruta, width=40)
combobox_inicio.grid(row=1, column=0, padx=5, pady=5)

tk.Label(frame_ruta, text="Fin:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
combobox_fin = ttk.Combobox(frame_ruta, width=40)
combobox_fin.grid(row=3, column=0, padx=5, pady=5)

calcular_btn = ttk.Button(frame_ruta, text="Calcular Ruta", command=calcular_ruta)
calcular_btn.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_ruta, text="Paradas:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
canvas_paradas = tk.Canvas(frame_ruta, height=200)
canvas_paradas.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

scrollbar = ttk.Scrollbar(frame_ruta, orient="vertical", command=canvas_paradas.yview)
scrollbar.grid(row=5, column=2, sticky="ns")

frame_paradas = ttk.Frame(canvas_paradas)
canvas_paradas.configure(yscrollcommand=scrollbar.set)
canvas_paradas.create_window((0, 0), window=frame_paradas, anchor="nw")
frame_paradas.bind("<Configure>", lambda e: canvas_paradas.configure(scrollregion=canvas_paradas.bbox("all")))

# Vincular la rueda del mouse al canvas
canvas_paradas.bind_all("<MouseWheel>", _on_mousewheel)

# Frame para resultados
frame_resultados = ttk.LabelFrame(ventana, text="Resultados", padding=10)
frame_resultados.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

tk.Label(frame_resultados, text="Orden de Paradas:").pack(pady=5)
lista_orden = tk.Listbox(frame_resultados, width=50, height=10)
lista_orden.pack(pady=5, fill="both", expand=True)

# Configurar pesos de las filas y columnas
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_rowconfigure(1, weight=1)
ventana.grid_columnconfigure(0, weight=1)
ventana.grid_columnconfigure(1, weight=1)

frame_ruta.grid_rowconfigure(5, weight=1)  # Permitir que el canvas se expanda

# Crear archivo CSV si no existe
try:
    with open('clientes.csv', mode='x', newline='', encoding='utf-8') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(['Nombre', 'Latitud', 'Longitud'])
except FileExistsError:
    pass

# Actualizar al iniciar
check_vars = []
actualizar_listas()

ventana.mainloop()
