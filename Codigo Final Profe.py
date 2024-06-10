import serial
import tkinter as tk
from tkinter import messagebox, ttk
import csv
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuración de la conexión serial
SERIAL_PORT = "COM4"  # Cambia esto al puerto correcto
BAUD_RATE = 9600

# Variables globales para los datos
times = []
temperatures = []
humidities = []

# Función para actualizar los gráficos
def plot_data():
    if times and temperatures and humidities:
        temp_ax.clear()
        hum_ax.clear()
        
        temp_ax.plot(times, temperatures, label="Temperatura (°C)", color="red")
        temp_ax.set_title("Temperatura vs Tiempo")
        temp_ax.set_xlabel("Tiempo (s)")
        temp_ax.set_ylabel("Temperatura (°C)")
        temp_ax.legend()
        temp_ax.grid(True)
        
        hum_ax.plot(times, humidities, label="Humedad (%)", color="blue")
        hum_ax.set_title("Humedad vs Tiempo")
        hum_ax.set_xlabel("Tiempo (s)")
        hum_ax.set_ylabel("Humedad (%)")
        hum_ax.legend()
        hum_ax.grid(True)
        
        temp_canvas.draw()
        hum_canvas.draw()
    else:
        messagebox.showinfo("Información", "No hay datos para graficar.")

# Función para leer datos del puerto serie
def read_serial_data(serial_conn, num_samples, filename, status_label, sample_count_label, data_listbox):
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Tiempo (s)', 'Temperatura (°C)', 'Humedad (%)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames,delimiter=';')
            writer.writeheader()

            start_time = time.time()
            for i in range(num_samples):
                line = serial_conn.readline().decode('utf-8').strip()
                if "Temperatura:" in line and "Humedad:" in line:
                    try:
                        parts = line.split('\t')
                        temperature_str = parts[0].split(':')[1].strip().split(' ')[0]
                        humidity_str = parts[1].split(':')[1].strip().split(' ')[0]
                        temperature = float(temperature_str)
                        humidity = float(humidity_str)
                        current_time = round(time.time() - start_time, 2)  # Formato del tiempo a dos decimales
                        
                        # Guardar datos en listas globales
                        times.append(current_time)
                        temperatures.append(temperature)
                        humidities.append(humidity)
                        
                        writer.writerow({'Tiempo (s)': current_time, 
                                         'Temperatura (°C)': temperature, 
                                         'Humedad (%)': humidity})
                        csvfile.flush()  # Asegura que los datos se escriban en el archivo
                        
                        # Mostrar datos en el listbox
                        data_listbox.insert(tk.END, f"Muestra {i+1}: Tiempo={current_time}s, Temperatura={temperature}°C, Humedad={humidity}%")
                        
                        sample_count_label.config(text=f"Muestras tomadas: {i+1}")
                        print(f"Muestra {i+1}: Tiempo={current_time}s, Temperatura={temperature}°C, Humedad={humidity}%")
                    except (ValueError, IndexError) as e:
                        print(f"Error procesando los datos: {line} -> {e}")
                else:
                    print(f"Formato de datos incorrecto: {line}")
                time.sleep(2)

        status_label.config(text="La toma de muestras ha finalizado.")
        messagebox.showinfo("Finalizado", f"El archivo {filename} se creó con éxito.")
    finally:
        serial_conn.close()

# Función para iniciar la toma de datos
def start_data_acquisition():
    try:
        num_samples = int(sample_entry.get())
        filename = file_entry.get()

        if not filename.endswith('.csv'):
            filename += '.csv'

        # Limpiar datos previos
        times.clear()
        temperatures.clear()
        humidities.clear()

        # Abrir conexión serial
        serial_conn = serial.Serial(SERIAL_PORT, BAUD_RATE)
        status_label.config(text="Iniciando toma de datos...")
        threading.Thread(target=read_serial_data, args=(serial_conn, num_samples, filename, status_label, sample_count_label, data_listbox)).start()
    except serial.SerialException as e:
        messagebox.showerror("Error de conexión", f"No se pudo abrir el puerto {SERIAL_PORT}. Error: {str(e)}")
    except ValueError:
        messagebox.showerror("Error de entrada", "Por favor ingrese un número válido de muestras.")

# Función para cerrar la aplicación
def close_application():
    root.destroy()

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Adquisición de Datos de Temperatura y Humedad")
root.geometry("1200x600")

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

left_frame = ttk.Frame(main_frame, padding="10")
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

right_frame = ttk.Frame(main_frame, padding="10")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Elementos del marco izquierdo
ttk.Label(left_frame, text="Nombre del archivo CSV:").pack(pady=5)
file_entry = ttk.Entry(left_frame, width=30)
file_entry.pack(pady=5)

ttk.Label(left_frame, text="Número de muestras:").pack(pady=5)
sample_entry = ttk.Entry(left_frame, width=30)
sample_entry.pack(pady=5)

start_button = ttk.Button(left_frame, text="Iniciar", command=start_data_acquisition)
start_button.pack(pady=5)

plot_button = ttk.Button(left_frame, text="Graficar", command=plot_data)
plot_button.pack(pady=5)

close_button = ttk.Button(left_frame, text="Cerrar", command=close_application)
close_button.pack(pady=5)

status_label = ttk.Label(left_frame, text="")
status_label.pack(pady=5)

sample_count_label = ttk.Label(left_frame, text="Muestras tomadas: 0")
sample_count_label.pack(pady=5)

data_label = ttk.Label(left_frame, text="Datos leídos:")
data_label.pack(pady=5)

data_listbox = tk.Listbox(left_frame, width=80, height=20)
data_listbox.pack(pady=5)

# Crear los gráficos
fig, (temp_ax, hum_ax) = plt.subplots(2, 1, figsize=(8, 6))
fig.tight_layout(pad=3.0)

# Inicializar los gráficos en blanco
temp_ax.set_title("Temperatura vs Tiempo")
temp_ax.set_xlabel("Tiempo (s)")
temp_ax.set_ylabel("Temperatura (°C)")
temp_ax.grid(True)

hum_ax.set_title("Humedad vs Tiempo")
hum_ax.set_xlabel("Tiempo (s)")
hum_ax.set_ylabel("Humedad (%)")
hum_ax.grid(True)

temp_canvas = FigureCanvasTkAgg(fig, master=right_frame)
temp_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

hum_canvas = FigureCanvasTkAgg(fig, master=right_frame)
hum_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

root.mainloop()
