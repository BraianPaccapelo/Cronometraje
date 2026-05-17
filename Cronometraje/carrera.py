import validaciones
import time
from datetime import timedelta
import sqlite3
from corredores import Corredores
import requests

resultados = []
corredores = []

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

conexion.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS resultados (
    numero_remera INTEGER,
    nombre TEXT,
    tiempo TEXT,
    sincronizado INTEGER DEFAULT 0
)
""")

conexion.commit()



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

        except:

            print("No hay conexión con el servidor.")
def pedir_talle():
    """
    Talles válidos
    """

    talles_validos = ["XS", "S", "M", "L", "XL", "XXL"]

    while True:

        talle = input(
            "Talle remera (XS/S/M/L/XL/XXL): "
        ).strip().upper()

        if talle in talles_validos:
            return talle

        print("ERROR: Talle inválido.")
def numero_remera_existente(numero):

    for corredor in corredores:

        if corredor.numero_remera == numero:
            return True

    return False
def pedir_numero(mensaje):
    """
    Solo números enteros
    """

    while True:

        dato = input(mensaje).strip()

        if dato.isdigit():
            return int(dato)

        print("ERROR: Debe ingresar solo números.")
def pedir_numero_remera(corredores):
    """
    Número de remera válido y no repetido
    """

    while True:
        numero = pedir_numero("Número de remera: ")

        if numero <= 0:
            print("ERROR: El número de remera debe ser mayor a 0.")
            continue

        # Verificar si el número de remera ya existe en la lista de corredores
        if any(corredor.numero_remera == numero for corredor in corredores):
            print("ERROR: Ese número de remera ya está registrado.")
            continue

        return numero
cursor.execute("SELECT * FROM corredores")

datos = cursor.fetchall()

for fila in datos:

    corredor = Corredores(
        fila[0],
        fila[1],
        fila[2],
        fila[3],
        fila[4],
        fila[5],
        fila[6],
        fila[7],
        fila[8],
        fila[9],
        fila[10]
    )

    corredores.append(corredor)
print("Corredores cargados correctamente.\n")

    


print("1.Registrar nuevo corredor")
print ("2.Iniciar cronometraje")


y = int(input("Seleccione una opción: "))
if (y == 1):
        dni = input("DNI: ")
        apellido = validaciones.pedir_texto("Apellido: ")
        nombre = validaciones.pedir_texto("Nombre: ")
        sexo = validaciones.pedir_sexo()
        ciudad = input("Ciudad: ").strip()
        edad = int(input("Edad: "))
        team = input("Team: ").strip()
        distancia = validaciones.pedir_distancia()
        talle = pedir_talle()
        categoria = validaciones.pedir_categoria()
        numero_remera = pedir_numero_remera(corredores)

        nuevo_corredor = Corredores(dni, apellido, nombre, sexo, ciudad, edad, team, distancia, talle, categoria, numero_remera)

        corredores.append(nuevo_corredor)

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

        print("Guardado en SQLite correctamente")

        
        
if y == 2:

    z = input("¿Desea iniciar el cronometraje? (y/n): ".lower())

    if z == "y":

        inicio = time.time()

        while z == "y":

            entrada = input("Ingrese número de remera o 'stop': ").lower()

            if entrada == "stop":

                z = "n"


            else:

                x = int(entrada)

                for corredor in corredores:

                    if corredor.numero_remera == x:

                        cursor.execute(
                            "SELECT * FROM resultados WHERE numero_remera = ?",
                            (x,)
                        )

                        ya_llego = cursor.fetchone()

                        if ya_llego:

                            print("Ese corredor ya registró llegada")

                        else:

                            actual = time.time()

                            transcurrido = actual - inicio

                            tiempo_formateado = timedelta(seconds=transcurrido)

                            resultados.append(corredor)

                            resultados.append(tiempo_formateado)

                            cursor.execute("""
                            INSERT INTO resultados
                            VALUES (?, ?, ?, ?)
                            """, (
                                corredor.numero_remera,
                                corredor.nombre,
                                str(tiempo_formateado),
                                0
                            ))

                            conexion.commit()

                            print(
                                corredor.numero_remera,
                                corredor.nombre,
                                "- Tiempo:",
                                tiempo_formateado
                            )

                            sincronizar_resultados()