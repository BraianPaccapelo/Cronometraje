import customtkinter as ctk
import time
from datetime import timedelta, datetime
from tkinter import messagebox
import mysql.connector
from db import get_conexion, CARRERA_ID

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1000x700")
app.title("Sistema de Cronometraje")

# =========================
# VARIABLES
# =========================

inicio = None
cronometro_activo = False

# =========================
# FUNCIONES
# =========================

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

    numero_dorsal  = int(entrada)
    conexion_mysql = None
    cursor_mysql   = None

    try:
        conexion_mysql = get_conexion()
        cursor_mysql   = conexion_mysql.cursor()

        cursor_mysql.execute("""
            SELECT i.id, c.nombre
            FROM inscripciones i
            JOIN corredores c ON i.corredor_id = c.id
            JOIN distancias d  ON i.distancia_id = d.id
            WHERE i.numero_dorsal = %s AND d.carrera_id = %s
        """, (numero_dorsal, CARRERA_ID))

        inscripcion = cursor_mysql.fetchone()

        if inscripcion is None:
            messagebox.showerror("Error", "Corredor no encontrado")
            return

        inscripcion_id = inscripcion[0]
        nombre         = inscripcion[1]

        cursor_mysql.execute(
            "SELECT id FROM llegadas WHERE inscripcion_id = %s",
            (inscripcion_id,)
        )
        if cursor_mysql.fetchone():
            messagebox.showerror("Error", "Ese corredor ya registró llegada")
            return

        tiempo_llegada = datetime.now()

        cursor_mysql.execute("""
            INSERT INTO llegadas (inscripcion_id, usuario_id, tiempo_llegada, metodo_carga)
            VALUES (%s, %s, %s, %s)
        """, (inscripcion_id, None, tiempo_llegada, 'manual'))

        conexion_mysql.commit()

        textbox_resultados.insert(
            "end",
            f"{numero_dorsal} - {nombre} - {tiempo_llegada.strftime('%H:%M:%S')}\n"
        )
        textbox_resultados.see("end")
        entry_remera.delete(0, "end")

    except mysql.connector.Error as e:
        messagebox.showerror("Error de base de datos", str(e))

    finally:
        if cursor_mysql:
            cursor_mysql.close()
        if conexion_mysql:
            conexion_mysql.close()


# =========================
# REGISTRO DE CORREDORES
# =========================

def guardar_corredor():

    conexion_mysql = None
    cursor_mysql = None

    try:
        dni              = entry_dni.get().strip()
        apellido         = entry_apellido.get().strip()
        nombre           = entry_nombre.get().strip()
        sexo             = combo_sexo.get()
        ciudad           = entry_ciudad.get().strip()
        fecha_str        = entry_fecha_nacimiento.get().strip()
        team             = entry_team.get().strip()
        distancia_nombre = combo_distancia.get()
        talle            = combo_talle.get()
        numero_remera    = int(entry_numero.get().strip())

        try:
            fecha_nacimiento = datetime.strptime(fecha_str, "%d/%m/%Y").date()
        except ValueError:
            messagebox.showerror("Error", "Fecha inválida. Use el formato dd/mm/aaaa")
            return

        conexion_mysql = get_conexion()
        cursor_mysql = conexion_mysql.cursor()

        cursor_mysql.execute(
            "SELECT id FROM inscripciones WHERE numero_dorsal = %s",
            (numero_remera,)
        )
        if cursor_mysql.fetchone():
            messagebox.showerror("Error", "Ese número de remera ya existe")
            return

        distancia_map = {"6KM": 6.00, "12KM": 12.00, "18KM": 18.00}
        cursor_mysql.execute(
            "SELECT id FROM distancias WHERE carrera_id = %s AND distancia_km = %s",
            (CARRERA_ID, distancia_map[distancia_nombre])
        )
        row = cursor_mysql.fetchone()
        if not row:
            messagebox.showerror("Error", "Distancia no encontrada en la base de datos")
            return
        distancia_id = row[0]

        cursor_mysql.execute("""
            INSERT INTO corredores (dni, apellido, nombre, sexo, ciudad, fecha_nacimiento, team, talle_remera, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (dni, apellido, nombre, sexo, ciudad, fecha_nacimiento, team, talle, 1))

        corredor_id = cursor_mysql.lastrowid

        cursor_mysql.execute("""
            INSERT INTO inscripciones (corredor_id, distancia_id, numero_dorsal, estado)
            VALUES (%s, %s, %s, %s)
        """, (corredor_id, distancia_id, numero_remera, 'inscripto'))

        conexion_mysql.commit()
        messagebox.showinfo("Éxito", "Corredor registrado correctamente")

    except mysql.connector.Error as e:
        messagebox.showerror("Error de base de datos", str(e))

    finally:
        if cursor_mysql:
            cursor_mysql.close()
        if conexion_mysql:
            conexion_mysql.close()


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

entry_fecha_nacimiento = ctk.CTkEntry(frame_der, placeholder_text="Fecha de nacimiento (dd/mm/aaaa)")
entry_fecha_nacimiento.pack(pady=5)

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
