import corredores
import validaciones
import time
from datetime import timedelta
import csv
from corredores import Corredores

resultados = []
corredores = []

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
with open("corredores.csv", newline="", encoding="utf-8") as archivo:

    lector = csv.DictReader(archivo)

    for fila in lector:

        corredor = Corredores(fila["dni"],fila["apellido"],fila["nombre"],fila["sexo"],fila["ciudad"],int(fila["edad"]),fila["team"],fila["distancia"],fila["talle"],fila["categoria"],int(fila["numero_remera"]))

        corredores.append(corredor)
print("Corredores cargados correctamente.\n")
for corredor in corredores:
    print(corredor.numero_remera,corredor.nombre,corredor.apellido,corredor.distancia)


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
        numero_remera = pedir_numero_remera()
        nuevo_corredor = Corredores(dni, apellido, nombre, sexo, ciudad, edad, team, distancia, talle, categoria, numero_remera)
        corredores.append(nuevo_corredor)
        with open("corredores.csv", "a", newline="", encoding="utf-8") as archivo:

            escritor = csv.writer(archivo)

            escritor.writerow([dni,apellido,nombre,sexo,ciudad,edad,team,distancia,talle,categoria,numero_remera])
            print("Guardado en CSV correctamente")
        
        
if y == 2:

    z = input("¿Desea iniciar el cronometraje? (y/n): ".lower())

    if z == "y":

        inicio = time.time()

        while z == "y":

            entrada = input("Ingrese número de remera o 'stop': ").lower()

            if entrada == "stop":

                print(corredor.numero_remera,corredor.nombre,"- Tiempo:",tiempo_formateado)

                z = "n"


            else:

                x = int(entrada)

                for corredor in corredores:

                    if corredor.numero_remera == x:

                        actual = time.time()

                        transcurrido = actual - inicio

                        tiempo_formateado = timedelta(seconds=transcurrido)

                        resultados.append(corredor)

                        resultados.append(tiempo_formateado)

                        print(corredor.numero_remera,corredor.nombre,"- Tiempo:",tiempo_formateado)