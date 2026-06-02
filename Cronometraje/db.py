import mysql.connector

CARRERA_ID = 1

def get_conexion():
    return mysql.connector.connect(
        host     = "localhost",
        port     = 3306,
        database = "atletismo",
        user     = "root",
        password = "qOP5JGOb#$48AV"
    )