from flask import Flask, request

app = Flask(__name__)

resultados_web = []

@app.route("/resultado", methods=["POST"])
def recibir_resultado():

    datos = request.json

    resultados_web.append(datos)

    print("Resultado recibido:")
    print(datos)

    return {
        "mensaje": "Resultado recibido"
    }, 200

@app.route("/")
def tabla_posiciones():

    html = """
    <h1>Tabla de posiciones</h1>
    <table border='1' cellpadding='10'>
        <tr>
            <th>Número</th>
            <th>Nombre</th>
            <th>Tiempo</th>
        </tr>
    """

    for resultado in resultados_web:

        html += f"""
        <tr>
            <td>{resultado['numero_remera']}</td>
            <td>{resultado['nombre']}</td>
            <td>{resultado['tiempo']}</td>
        </tr>
        """

    html += "</table>"

    return html

if __name__ == "__main__":
    app.run(debug=True)