import sqlite3
import random
import tkinter as tk
from tkinter import messagebox, simpledialog

class Animal:
    def __init__(self, id, nombre, caracteristicas):
        self.id = id
        self.nombre = nombre
        self.caracteristicas = caracteristicas

class JuegoAdivinaQuien:
    def __init__(self):
        self.personajes = self.cargar_personajes()
        self.caracteristicas_preguntadas = set()
        self.pregunta_actual = None

    def cargar_personajes(self):
        conexion = sqlite3.connect('animales.db')
        cursor = conexion.cursor()

        cursor.execute('SELECT * FROM animales')
        animales = cursor.fetchall()
        personajes = []

        for animal in animales:
            animal_id, nombre = animal
            cursor.execute('SELECT caracteristica FROM caracteristicas WHERE animal_id = ?', (animal_id,))
            caracteristicas = [car[0] for car in cursor.fetchall()]
            personajes.append(Animal(animal_id, nombre, caracteristicas))

        conexion.close()
        return personajes

    def hacer_pregunta(self):
        if not self.personajes:
            return None
        posibles_caracteristicas = {car for personaje in self.personajes for car in personaje.caracteristicas}
        caracteristicas_disponibles = list(posibles_caracteristicas - self.caracteristicas_preguntadas)
        if not caracteristicas_disponibles:
            return None
        self.pregunta_actual = random.choice(caracteristicas_disponibles)
        self.caracteristicas_preguntadas.add(self.pregunta_actual)
        return self.pregunta_actual

    def filtrar_personajes(self, respuesta):
        if self.pregunta_actual:
            if respuesta == "si":
                self.personajes = [personaje for personaje in self.personajes if self.pregunta_actual in personaje.caracteristicas]
            elif respuesta == "no":
                self.personajes = [personaje for personaje in self.personajes if self.pregunta_actual not in personaje.caracteristicas]

    def adivinar_personaje(self):
        if len(self.personajes) == 1:
            return self.personajes[0].nombre
        return None

    def aprender_nuevo_animal(self, nombre, caracteristicas):
        conexion = sqlite3.connect('animales.db')
        cursor = conexion.cursor()

        cursor.execute('INSERT INTO animales (nombre) VALUES (?)', (nombre,))
        animal_id = cursor.lastrowid
        for caracteristica in caracteristicas:
            cursor.execute('INSERT INTO caracteristicas (animal_id, caracteristica) VALUES (?, ?)', (animal_id, caracteristica))

        conexion.commit()
        conexion.close()

class InterfazJuego:
    def __init__(self, root):
        self.juego = JuegoAdivinaQuien()
        self.root = root
        self.root.title("Adivina Quién - Animales")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f8ff')

        self.frame = tk.Frame(root, bg='#f0f8ff')
        self.frame.pack(pady=20)

        self.label_pregunta = tk.Label(self.frame, text="Piensa en un animal y responde a las siguientes preguntas con 'sí' o 'no':", bg='#f0f8ff', font=('Helvetica', 12))
        self.label_pregunta.pack(pady=10)

        self.boton_si = tk.Button(self.frame, text="Sí", command=lambda: self.responder("si"), width=10, bg='#32cd32', fg='white', font=('Helvetica', 10, 'bold'))
        self.boton_no = tk.Button(self.frame, text="No", command=lambda: self.responder("no"), width=10, bg='#ff4500', fg='white', font=('Helvetica', 10, 'bold'))
        
        self.boton_si.pack(side=tk.LEFT, padx=20, pady=20)
        self.boton_no.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.hacer_nueva_pregunta()

    def hacer_nueva_pregunta(self):
        pregunta = self.juego.hacer_pregunta()
        if pregunta:
            self.label_pregunta.config(text=f"¿El animal tiene la siguiente característica? \n{pregunta}")
        else:
            self.terminar_juego()

    def responder(self, respuesta):
        self.juego.filtrar_personajes(respuesta)
        animal_adivinado = self.juego.adivinar_personaje()
        if animal_adivinado:
            self.label_pregunta.config(text=f"¡El animal es {animal_adivinado}!")
            self.preguntar_si_correcto(animal_adivinado)
        elif not self.juego.personajes:
            self.label_pregunta.config(text="No pude adivinar el animal.")
            self.aprender_nuevo_animal()
        else:
            self.hacer_nueva_pregunta()

    def preguntar_si_correcto(self, animal_adivinado):
        respuesta = messagebox.askyesno("Adivinanza", f"¿Adiviné correctamente? ¿Es {animal_adivinado}?")
        if not respuesta:
            self.aprender_nuevo_animal()
        else:
            self.jugar_nuevamente()

    def aprender_nuevo_animal(self):
        nombre = simpledialog.askstring("Nuevo Animal", "¿Cuál es el nombre del animal en el que estabas pensando?")
        if nombre:
            caracteristicas = []
            for i in range(3):
                caracteristica = simpledialog.askstring("Nueva Característica", f"Dime una característica de {nombre}")
                if caracteristica:
                    caracteristicas.append(caracteristica)
            self.juego.aprender_nuevo_animal(nombre, caracteristicas)
            messagebox.showinfo("Gracias", f"¡Gracias! Ahora sé más sobre {nombre}.")
            self.jugar_nuevamente()

    def terminar_juego(self):
        messagebox.showinfo("Fin del Juego", "Ya se han preguntado todas las características posibles.")
        self.jugar_nuevamente()

    def jugar_nuevamente(self):
        respuesta = messagebox.askyesno("Jugar Nuevamente", "¿Quieres volver a jugar?")
        if respuesta:
            self.root.destroy()
            root = tk.Tk()
            app = InterfazJuego(root)
            root.mainloop()
        else:
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazJuego(root)
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazJuego(root)
    root.mainloop()
