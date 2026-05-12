import customtkinter as ctk
from tkinter import messagebox
from validaciones import pedir_numero_remera, pedir_texto, pedir_sexo, pedir_distancia, pedir_categoria
from corredores import Corredores

# Lista de corredores (simulación de la lista en validaciones)
corredores = []

# Configuración de la ventana principal
ctk.set_appearance_mode("System")  # Modo de apariencia (System, Dark, Light)
ctk.set_default_color_theme("blue")  # Tema de color

class InterfazCorredores(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestión de Corredores")
        self.geometry("500x600")

        # Etiqueta de título
        self.label_titulo = ctk.CTkLabel(self, text="Registro de Corredores", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.pack(pady=10)

        # Campos de entrada
        self.entry_dni = ctk.CTkEntry(self, placeholder_text="DNI")
        self.entry_dni.pack(pady=5)

        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Nombre")
        self.entry_nombre.pack(pady=5)

        self.entry_apellido = ctk.CTkEntry(self, placeholder_text="Apellido")
        self.entry_apellido.pack(pady=5)

        self.entry_ciudad = ctk.CTkEntry(self, placeholder_text="Ciudad")
        self.entry_ciudad.pack(pady=5)

        self.entry_edad = ctk.CTkEntry(self, placeholder_text="Edad")
        self.entry_edad.pack(pady=5)

        self.entry_team = ctk.CTkEntry(self, placeholder_text="Team")
        self.entry_team.pack(pady=5)

        self.entry_numero_remera = ctk.CTkEntry(self, placeholder_text="Número de Remera")
        self.entry_numero_remera.pack(pady=5)

        # Botones para seleccionar sexo, distancia y categoría
        self.button_sexo = ctk.CTkButton(self, text="Seleccionar Sexo", command=self.seleccionar_sexo)
        self.button_sexo.pack(pady=5)

        self.button_distancia = ctk.CTkButton(self, text="Seleccionar Distancia", command=self.seleccionar_distancia)
        self.button_distancia.pack(pady=5)

        self.button_categoria = ctk.CTkButton(self, text="Seleccionar Categoría", command=self.seleccionar_categoria)
        self.button_categoria.pack(pady=5)

        # Botón para registrar corredor
        self.button_registrar = ctk.CTkButton(self, text="Registrar Corredor", command=self.registrar_corredor)
        self.button_registrar.pack(pady=10)

        # Lista de corredores registrados
        self.label_lista = ctk.CTkLabel(self, text="Corredores Registrados:", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_lista.pack(pady=10)

        self.text_lista = ctk.CTkTextbox(self, height=200)
        self.text_lista.pack(pady=5)

    def seleccionar_sexo(self):
        self.sexo = pedir_sexo()
        messagebox.showinfo("Sexo Seleccionado", f"Sexo: {self.sexo}")

    def seleccionar_distancia(self):
        self.distancia = pedir_distancia()
        messagebox.showinfo("Distancia Seleccionada", f"Distancia: {self.distancia}")

    def seleccionar_categoria(self):
        self.categoria = pedir_categoria()
        messagebox.showinfo("Categoría Seleccionada", f"Categoría: {self.categoria}")

    def registrar_corredor(self):
        try:
            dni = self.entry_dni.get()
            nombre = pedir_texto(self.entry_nombre.get())
            apellido = pedir_texto(self.entry_apellido.get())
            ciudad = self.entry_ciudad.get()
            edad = int(self.entry_edad.get())
            team = self.entry_team.get()
            numero_remera = int(self.entry_numero_remera.get())

            # Validar número de remera
            if any(corredor.numero_remera == numero_remera for corredor in corredores):
                messagebox.showerror("Error", "El número de remera ya está registrado.")
                return

            # Crear y agregar corredor
            nuevo_corredor = Corredores(dni, apellido, nombre, self.sexo, ciudad, edad, team, self.distancia, "M", self.categoria, numero_remera)
            corredores.append(nuevo_corredor)

            # Actualizar lista de corredores
            self.actualizar_lista()
            messagebox.showinfo("Éxito", "Corredor registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar corredor: {e}")

    def actualizar_lista(self):
        self.text_lista.delete("1.0", "end")
        for corredor in corredores:
            self.text_lista.insert("end", f"{corredor.numero_remera}: {corredor.nombre} {corredor.apellido} - {corredor.distancia}\n")

# Ejecutar la interfaz
if __name__ == "__main__":
    app = InterfazCorredores()
    app.mainloop()