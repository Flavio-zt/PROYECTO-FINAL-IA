import tkinter as tk
from tkinter import messagebox, ttk
from gtts import gTTS
import os
import pandas as pd
import pygame
from datetime import datetime
from PIL import Image, ImageTk  # Necesario para manejar imágenes
import speech_recognition as sr


# Cargar el dataset
dataset_tts = pd.read_csv('dataset_tts.csv')

# Crear la carpeta 'audio' si no existe
audio_folder = 'audio'
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)

# Obtener el conjunto de textos válidos del dataset
valid_texts = set(dataset_tts['Texto'].tolist())

# Inicializar pygame para la reproducción de audio
pygame.mixer.init()


# Asegúrate de que 'play.png' y 'pause.png' están en el directorio del proyecto.


def text_to_speech(text, filename=None):
    if not filename:
        filename = f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    elif not filename.endswith('.mp3'):
        filename += '.mp3'
    filepath = os.path.join(audio_folder, filename)
    tts = gTTS(text=text, lang='es')  # Cambiar el idioma a español
    tts.save(filepath)
    return filepath

def play_audio(filepath):
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

def pause_audio():
    pygame.mixer.music.pause()

def unpause_audio():
    pygame.mixer.music.unpause()

def stop_audio():
    pygame.mixer.music.stop()

def open_text_to_speech_window():
    # Crear una nueva ventana para la conversión de texto a voz
    text_to_speech_window = tk.Toplevel(root)
    text_to_speech_window.title("Texto a Voz")
    text_to_speech_window.geometry("500x400")
    text_to_speech_window.configure(bg='#f0f0f0')

    # Etiqueta y combobox para seleccionar texto
    text_combobox_label = tk.Label(text_to_speech_window, text="Selecciona un texto:", font=("Arial", 12), bg='#f0f0f0')
    text_combobox_label.pack(pady=10)

    text_combobox = ttk.Combobox(text_to_speech_window, values=dataset_tts['Texto'].tolist(), font=("Arial", 12))
    text_combobox.pack(pady=10)

    # Entrada para el nombre del archivo
    filename_entry = tk.Entry(text_to_speech_window, font=("Arial", 12))
    #filename_entry.pack(pady=5)

    # Botón para realizar la conversión
    convert_button = tk.Button(text_to_speech_window, text="Convertir a Voz", font=("Arial", 14), bg='#4CAF50', fg='#ffffff', padx=20, pady=10,
                               command=lambda: on_convert_button_click(text_combobox.get(), filename_entry.get().strip(), text_to_speech_window))
    convert_button.pack(pady=20)

    # Reproductor de audio con un solo botón
    global audio_control_button
    audio_control_button = tk.Button(text_to_speech_window, image=None, bg='#f0f0f0', command=toggle_audio)
    audio_control_button.pack(pady=20)

    # Cargar los iconos
    load_icons()

def load_icons():
    global play_icon, pause_icon, stop_icon
    play_icon = ImageTk.PhotoImage(Image.open('play.png'))
    pause_icon = ImageTk.PhotoImage(Image.open('pause.png'))
    stop_icon = ImageTk.PhotoImage(Image.open('stop.png'))

def update_audio_control_button(state):
    if state == 'playing':
        audio_control_button.config(image=pause_icon, command=pause_audio)
    elif state == 'paused':
        audio_control_button.config(image=play_icon, command=unpause_audio)
    elif state == 'stopped':
        audio_control_button.config(image=play_icon, command=play_audio)

def toggle_audio():
    global current_filepath, audio_state
    if audio_state == 'stopped' or audio_state == 'paused':
        play_audio(current_filepath)
        update_audio_control_button('playing')
        audio_state = 'playing'
    elif audio_state == 'playing':
        pause_audio()
        update_audio_control_button('paused')
        audio_state = 'paused'

def on_convert_button_click(selected_text, filename, window):
    global current_filepath, audio_state
    if selected_text in valid_texts:
        current_filepath = text_to_speech(selected_text, filename)
        play_audio(current_filepath)  # Reproduce el audio automáticamente
        update_audio_control_button('playing')  # Cambia el botón a 'playing'
        audio_state = 'playing'
        messagebox.showinfo("Texto a Voz", f"Conversión completada y guardada como '{filename or 'output_<timestamp>.mp3'}' en la carpeta 'audio'.")
    else:
        messagebox.showwarning("Advertencia", "El texto seleccionado no está en el dataset.")

def open_speech_to_text_window():
    # Crear una nueva ventana para la conversión de voz a texto
    speech_to_text_window = tk.Toplevel(root)
    speech_to_text_window.title("Voz a Texto")
    speech_to_text_window.geometry("500x400")
    speech_to_text_window.configure(bg='#f0f0f0')

    # Área de texto para mostrar el resultado
    result_text = tk.Text(speech_to_text_window, height=10, width=50, wrap=tk.WORD, font=("Arial", 12))
    result_text.pack(pady=20)
    result_text.insert(tk.END, "Aquí se mostrará el resultado de la conversión.")

    # Botón para iniciar la conversión
    start_button = tk.Button(speech_to_text_window, text="Grabar y Convertir", font=("Arial", 14), bg='#2196F3', fg='#ffffff', padx=20, pady=10,
                             command=lambda: on_start_recording(result_text, speech_to_text_window))
    start_button.pack(pady=20)


def on_start_recording(result_text, window):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Informar al usuario que está grabando
        messagebox.showinfo("Grabación", "Habla ahora. Te escucharé.")
        audio_data = recognizer.listen(source)  # Escuchar el audio del micrófono

        try:
            # Convertir el audio a texto
            text = recognizer.recognize_google(audio_data, language='es-ES')
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, text)
            messagebox.showinfo("Voz a Texto", "Conversión completada.")
        except sr.UnknownValueError:
            messagebox.showwarning("Error", "No se pudo entender el audio.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"No se pudo conectar con el servicio de reconocimiento de voz; {e}")


# Crear la ventana principal
root = tk.Tk()
root.title("Aplicación de Conversión")
root.geometry("1000x700")  # Tamaño de la ventana ajustado
root.configure(bg='#f0f0f0')  # Color de fondo suave

# Título de la ventana
title_label = tk.Label(root, text="Opciones de Conversión", font=("Arial", 24, "bold"), bg='#f0f0f0')
title_label.pack(pady=30)

# Crear un marco para agrupar los elementos
frame = tk.Frame(root, bg='#ffffff', padx=20, pady=20, relief=tk.RAISED, borderwidth=2)
frame.pack(padx=30, pady=30, expand=True, fill=tk.BOTH)

# Texto de instrucciones
info_label = tk.Label(frame, text="Elige una opción:", font=("Arial", 16), bg='#ffffff')
info_label.pack(pady=20)

# Crear botones para las dos opciones
button_frame = tk.Frame(frame, bg='#ffffff')
button_frame.pack(pady=20)

text_to_speech_button = tk.Button(button_frame, text="Texto a Voz", font=("Arial", 14), bg='#4CAF50', fg='#ffffff', padx=20, pady=10, command=open_text_to_speech_window)
text_to_speech_button.pack(side=tk.LEFT, padx=10)

speech_to_text_button = tk.Button(button_frame, text="Voz a Texto", font=("Arial", 14), bg='#2196F3', fg='#ffffff', padx=20, pady=10, command=open_speech_to_text_window)
speech_to_text_button.pack(side=tk.LEFT, padx=10)

# Inicializar estado de audio
audio_state = 'stopped'

# Iniciar el bucle principal de la aplicación
root.mainloop()
