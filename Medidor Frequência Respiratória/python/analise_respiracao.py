import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque


PORTA = 'COM7'       # Substituir a porta
BAUDRATE = 9600

ser = serial.Serial(PORTA, BAUDRATE)

window_size = 100

signal = deque([0]*window_size, maxlen=window_size)
frequencies = deque([0]*window_size, maxlen=window_size)
min = deque([0]*window_size, maxlen=window_size)
max = deque([0]*window_size, maxlen=window_size)
threshold = deque([0]*window_size, maxlen=window_size)

plt.style.use('dark_background')
fig, ax = plt.subplots()
signal_line, = ax.plot([], [], color='lime', label='Sinal')
thresh_line, = ax.plot([], [], 'r--', linewidth=1.0, label='Threshold')
ax.set_ylim(200, 450)
ax.set_xlim(0, window_size)
ax.set_title("Sinal Respiratório", color='white', fontsize=14)
ax.set_ylabel("Valor ADC", color='white')
ax.set_xlabel("Tempo", color='white')
ax.legend(loc='upper right')

text_info = ax.text(0.02, 0.95, '', transform=ax.transAxes, verticalalignment='top', color='white', fontsize=12)

def update(frame):
    global signal, frequencies, min, max, threshold

    while ser.in_waiting:
        try:
            line = ser.readline().decode().strip()

            if not line or ";" not in line:
                return 

            parts = line.strip(";").split(";")
            if len(parts) != 5:
                print(f"Linha inválida: {line}")
                return

            mean = int(parts[0])
            rpm = int(parts[1])
            vmin = int(parts[2])
            vmax = int(parts[3])
            thresh = int(parts[4])

            signal.append(mean)
            frequencies.append(rpm)
            min.append(vmin)
            max.append(vmax)
            threshold.append(thresh)

            signal_line.set_data(range(len(signal)), signal)
            thresh_line.set_data(range(len(threshold)), threshold)
            text_info.set_text(
                f"Frequência Respiratória: {rpm} rpm\n"
                f"Mínimo: {vmin}\nMáximo: {vmax}\nThreshold: {thresh}"
            )

        except Exception as e:
            print(f"Erro ao processar linha: {e}")

    return signal_line, thresh_line, text_info

ani = animation.FuncAnimation(fig, update, interval=100, cache_frame_data=False)
plt.tight_layout()
plt.show()
