import tkinter as tk
from tkinter import messagebox, ttk


def show_settings_window(player):
    def update_parameters():
        # Define una lista de tuplas para iterar sobre los campos de entrada y sus respectivas variables
        fields = [
            (max_health_entry, "health"),
            (max_health_entry, "max_health"),
            (min_attack_entry, "min_attack"),
            (max_attack_entry, "max_attack"),
            (defense_entry, "defense")
        ]

        try:
            # Itera sobre los campos de entrada y sus variables correspondientes
            for field, attribute in fields:
                value = field.get()  # Obtiene el valor del campo de entrada
                if value:  # Verifica si se ingresó algún valor
                    # Verifica que el valor ingresado sea un entero positivo
                    if int(value) >= 0:
                        setattr(player, attribute, int(value))  # Actualiza el atributo correspondiente del jugador
                    else:
                        messagebox.showerror("Error", "Por favor, introduce un valor numérico positivo.")

            selected_effect = status_effect_combobox.get()  # Obtiene el efecto de estado seleccionado
            # Obtiene la duración del efecto de estado
            duration = int(duration_entry.get())

            if selected_effect:  # Verifica que se haya seleccionado un efecto de estado
                if selected_effect != "None":
                    # Verifica que la duración esté dentro del rango deseado (2-5)
                    if 2 <= duration <= 5:
                        player.status_effect = selected_effect  # Actualiza el efecto de estado
                        player.status_duration = duration  # Actualiza la duración del efecto de estado
                        messagebox.showinfo("Éxito", "¡Parámetros actualizados correctamente!")
                    else:
                        messagebox.showerror("Error", "La duración del efecto de estado debe estar entre 2 y 5.")
                else:
                    # Si el efecto de estado es "None", verifica si la duración es 0 para permitir la actualización
                    if duration == 0:
                        player.status_effect = selected_effect  # Actualiza el efecto de estado
                        player.status_duration = duration  # Actualiza la duración del efecto de estado
                        messagebox.showinfo("Éxito", "¡Parámetros actualizados correctamente!")
                    else:
                        messagebox.showerror("Error", "La duración del efecto de estado debe ser 0 si el efecto es None.")
            else:
                messagebox.showerror("Error", "Por favor, selecciona un efecto de estado.")
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce números válidos en los campos numéricos.")

    def center_window(window, width, height):
        # Obtener el ancho y alto de la pantalla
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calcular las coordenadas x e y para centrar la ventana
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer la geometría de la ventana
        window.geometry(f"{width}x{height}+{x}+{y}")

    # Crear la ventana principal
    settings_window = tk.Tk()
    settings_window.title("Ajustes del Juego")

    # Establecer el tamaño de la ventana
    window_width = 600  # Ancho de la ventana en píxeles
    window_height = 400  # Alto de la ventana en píxeles
    settings_window.geometry(f"{window_width}x{window_height}")

    # Centrar la ventana en la pantalla
    center_window(settings_window, window_width, window_height)

    # Crear una fuente con un tamaño específico
    custom_font = ("Helvetica", 11)

    # Crear campos de entrada para los parámetros
    max_health_label = tk.Label(settings_window, text="Salud Máxima del Jugador (Opcional):", font=custom_font)
    max_health_label.pack()
    max_health_entry = tk.Entry(settings_window, font=custom_font)
    max_health_entry.pack()

    min_attack_label = tk.Label(settings_window, text="Ataque Mínimo del Jugador (Opcional):", font=custom_font)
    min_attack_label.pack()
    min_attack_entry = tk.Entry(settings_window, font=custom_font)
    min_attack_entry.pack()

    max_attack_label = tk.Label(settings_window, text="Ataque Máximo del Jugador (Opcional):", font=custom_font)
    max_attack_label.pack()
    max_attack_entry = tk.Entry(settings_window, font=custom_font)
    max_attack_entry.pack()

    defense_entry_label = tk.Label(settings_window, text="Defensa del Jugador (Opcional):", font=custom_font)
    defense_entry_label.pack()
    defense_entry = tk.Entry(settings_window, font=custom_font)
    defense_entry.pack()

    # Opciones para el efecto de estado
    status_effect_options = ["None", "quemado", "paralizado", "envenenado", "congelado"]

    # Etiqueta y campo desplegable para el efecto de estado
    status_effect_label = tk.Label(settings_window, text="Efecto de Estado:", font=custom_font)
    status_effect_label.pack()
    status_effect_combobox = ttk.Combobox(settings_window, values=status_effect_options, font=custom_font, state="readonly")
    status_effect_combobox.current(0)  # Establece el primer elemento como seleccionado por defecto
    status_effect_combobox.pack()

    # Etiqueta y campo de entrada para la duración del efecto de estado
    duration_label = tk.Label(settings_window, text="Duración del Efecto de Estado:", font=custom_font)
    duration_label.pack()
    # Campo de entrada para la duración del efecto de estado
    duration_entry = tk.Entry(settings_window, font=custom_font)
    duration_entry.pack()
    # Establecer el valor predeterminado en el campo de entrada
    duration_entry.insert(0, "0")

    # Botón para actualizar los parámetros
    update_button = tk.Button(settings_window, text="Actualizar Parámetros", command=update_parameters, font=custom_font)
    update_button.pack()

    # Ejecutar el bucle principal de la interfaz gráfica
    settings_window.mainloop()
