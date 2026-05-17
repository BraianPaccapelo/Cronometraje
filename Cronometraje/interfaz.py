import customtkinter as ctk
import sqlite3
import requests
import time
from datetime import timedelta
from tkinter import messagebox
from corredores import Corredores

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1000x700")
app.title("Sistema de Cronometraje")

# =========================
# BASE DE DATOS
# =========================

conexion = sqlite3.connect("cronometraje.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS corredores (
    dni TEXT,
    apellido TEXT,
    nombre TEXT,
    sexo TEXT,
    ciudad TEXT,
    edad INTEGER,
    team TEXT,
    distancia TEXT,
    talle TEXT,
    categoria TEXT,
    numero_remera INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    numero_remera INTEGER,
    nombre TEXT,
    tiempo TEXT,
    sincronizado INTEGER DEFAULT 0
)
""")
conexion.commit()

# =========================
# VARIABLES
# =========================

inicio = None
cronometro_activo = False

# =========================
# FUNCIONES
# =========================

def sincronizar_resultados():

    cursor.execute("""
    SELECT rowid, numero_remera, nombre, tiempo
    FROM resultados
    WHERE sincronizado = 0
    """)

    pendientes = cursor.fetchall()

    for resultado in pendientes:

        rowid = resultado[0]

        datos = {
            "numero_remera": resultado[1],
            "nombre": resultado[2],
            "tiempo": resultado[3]
        }

        try:

            respuesta = requests.post(
                "http://127.0.0.1:5000/resultado",
                json=datos
            )

            if respuesta.status_code == 200:

                cursor.execute("""
                UPDATE resultados
                SET sincronizado = 1
                WHERE rowid = ?
                """, (rowid,))

                conexion.commit()

                print("Resultado sincronizado:", datos)

        except Exception as e:

            print(e)

def actualizar_cronometro():

    if cronometro_activo:

        actual = time.time()
        transcurrido = actual - inicio

        tiempo = str(timedelta(seconds=int(transcurrido)))

        label_cronometro.configure(text=tiempo)

        app.after(1000, actualizar_cronometro)


def iniciar_cronometro():

    global inicio
    global cronometro_activo

    inicio = time.time()
    cronometro_activo = True

    label_estado.configure(text="Cronómetro iniciado")

    actualizar_cronometro()


def detener_cronometro():

    global cronometro_activo

    cronometro_activo = False

    label_estado.configure(text="Cronómetro detenido")


def registrar_llegada(event=None):

    if not cronometro_activo:
        messagebox.showerror("Error", "El cronómetro no está iniciado")
        return

    entrada = entry_remera.get().strip()

    if not entrada.isdigit():
        messagebox.showerror("Error", "Ingrese un número válido")
        return

    numero_remera = int(entrada)

    cursor.execute(
        "SELECT * FROM corredores WHERE numero_remera = ?",
        (numero_remera,)
    )

    corredor = cursor.fetchone()

    if corredor is None:
        messagebox.showerror("Error", "Corredor no encontrado")
        return

    actual = time.time()
    transcurrido = actual - inicio

    tiempo_formateado = str(
        timedelta(seconds=int(transcurrido))
    )

    nombre = corredor[2]

    cursor.execute("""
    INSERT INTO resultados
    VALUES (?, ?, ?, ?)
    """, (
        numero_remera,
        nombre,
        tiempo_formateado,
        0
    ))

    conexion.commit()

    sincronizar_resultados()

    textbox_resultados.insert(
        "end",
        f"{numero_remera} - {nombre} - {tiempo_formateado}\n"
    )

    textbox_resultados.see("end")

    entry_remera.delete(0, "end")


# =========================
# REGISTRO DE CORREDORES
# =========================

def guardar_corredor():

    try:

        dni = entry_dni.get()
        apellido = entry_apellido.get()
        nombre = entry_nombre.get()
        sexo = combo_sexo.get()
        ciudad = entry_ciudad.get()
        edad = int(entry_edad.get())
        team = entry_team.get()
        distancia = combo_distancia.get()
        talle = combo_talle.get()
        categoria = combo_categoria.get()
        numero_remera = int(entry_numero.get())

        cursor.execute(
            "SELECT * FROM corredores WHERE numero_remera = ?",
            (numero_remera,)
        )

        existe = cursor.fetchone()

        if existe:
            messagebox.showerror(
                "Error",
                "Ese número de remera ya existe"
            )
            return

        cursor.execute("""
        INSERT INTO corredores
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dni,
            apellido,
            nombre,
            sexo,
            ciudad,
            edad,
            team,
            distancia,
            talle,
            categoria,
            numero_remera
        ))

        conexion.commit()

        messagebox.showinfo(
            "Éxito",
            "Corredor registrado correctamente"
        )

    except:
        messagebox.showerror(
            "Error",
            "Verifique los datos ingresados"
        )


# =========================
# INTERFAZ
# =========================

frame_izq = ctk.CTkFrame(app)
frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

frame_der = ctk.CTkFrame(app)
frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# =========================
# CRONOMETRO
# =========================

label_titulo = ctk.CTkLabel(
    frame_izq,
    text="CRONOMETRAJE",
    font=("Arial", 28, "bold")
)
label_titulo.pack(pady=10)

label_cronometro = ctk.CTkLabel(
    frame_izq,
    text="00:00:00",
    font=("Arial", 40, "bold")
)
label_cronometro.pack(pady=20)

label_estado = ctk.CTkLabel(
    frame_izq,
    text="Esperando inicio"
)
label_estado.pack(pady=10)

boton_iniciar = ctk.CTkButton(
    frame_izq,
    text="Iniciar",
    command=iniciar_cronometro
)
boton_iniciar.pack(pady=10)

boton_detener = ctk.CTkButton(
    frame_izq,
    text="Detener",
    command=detener_cronometro
)
boton_detener.pack(pady=10)

entry_remera = ctk.CTkEntry(
    frame_izq,
    placeholder_text="Número de remera"
)
entry_remera.pack(pady=20)

entry_remera.bind("<Return>", registrar_llegada)

boton_registrar = ctk.CTkButton(
    frame_izq,
    text="Registrar llegada",
    command=registrar_llegada
)
boton_registrar.pack(pady=10)

textbox_resultados = ctk.CTkTextbox(
    frame_izq,
    width=400,
    height=300
)
textbox_resultados.pack(pady=20)

# =========================
# REGISTRO
# =========================

label_registro = ctk.CTkLabel(
    frame_der,
    text="REGISTRO DE CORREDORES",
    font=("Arial", 24, "bold")
)
label_registro.pack(pady=10)

entry_dni = ctk.CTkEntry(frame_der, placeholder_text="DNI")
entry_dni.pack(pady=5)

entry_apellido = ctk.CTkEntry(frame_der, placeholder_text="Apellido")
entry_apellido.pack(pady=5)

entry_nombre = ctk.CTkEntry(frame_der, placeholder_text="Nombre")
entry_nombre.pack(pady=5)

combo_sexo = ctk.CTkComboBox(frame_der, values=["M", "F"])
combo_sexo.pack(pady=5)

entry_ciudad = ctk.CTkEntry(frame_der, placeholder_text="Ciudad")
entry_ciudad.pack(pady=5)

entry_edad = ctk.CTkEntry(frame_der, placeholder_text="Edad")
entry_edad.pack(pady=5)

entry_team = ctk.CTkEntry(frame_der, placeholder_text="Team")
entry_team.pack(pady=5)

combo_distancia = ctk.CTkComboBox(
    frame_der,
    values=["6KM", "12KM", "18KM"]
)
combo_distancia.pack(pady=5)

combo_talle = ctk.CTkComboBox(
    frame_der,
    values=["XS", "S", "M", "L", "XL", "XXL"]
)
combo_talle.pack(pady=5)

combo_categoria = ctk.CTkComboBox(
    frame_der,
    values=[
        "16-19", "20-24", "25-29",
        "30-34", "35-39", "40-44",
        "45-49", "50-54", "55-59",
        "60-64", "65-69", "70"
    ]
)
combo_categoria.pack(pady=5)

entry_numero = ctk.CTkEntry(
    frame_der,
    placeholder_text="Número de remera"
)
entry_numero.pack(pady=5)

boton_guardar = ctk.CTkButton(
    frame_der,
    text="Guardar corredor",
    command=guardar_corredor
)
boton_guardar.pack(pady=20)

app.mainloop()
