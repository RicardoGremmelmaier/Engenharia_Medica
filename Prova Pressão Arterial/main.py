import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

file_path = 'dataset/RicardoGremme.txt'

# Leitura dos dados
pressure_values = []
with open(file_path, 'r') as f:
    for line in f:
        parts = line.strip().split(';')
        if len(parts) == 2:
            try:
                time = int(parts[0].strip())
                value = int(parts[1].strip())
                pressure_values.append((time, value))
            except ValueError:
                continue

# Separar listas de tempo e valor
times, pressures = zip(*pressure_values)

# Plotar o gráfico da pressão ao longo do tempo
plt.figure(figsize=(12, 5))
plt.plot(pressures, label='Pressão detectada (bruta)', color='blue')
plt.title('Leitura do Sensor de Pressão')
plt.xlabel('Amostra')
plt.ylabel('Valor do Sensor')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

pressures_np = np.array(pressures)

# Aplica média móvel
window = 50  
moving_average = np.convolve(pressures_np, np.ones(window)/window, mode='same')

# Sinal oscilatório = sinal original - tendência

osc = pressures_np - moving_average
start = 1500
end = 5000
osc_util = osc[start:end]

# Detectar picos (batimentos)
sampling_rate = 45  
max_bpm = 110
min_dist_amostras = int(sampling_rate * 60 / max_bpm)
amplitude_max = np.max(osc_util) - np.min(osc_util)
prominencia_min = amplitude_max * 0.2  
min_distance = int(sampling_rate / 3)
peaks_rel, _ = find_peaks(osc_util, distance=min_distance, prominence=prominencia_min)
peaks = peaks_rel + start

# Calcular BPM com base nos intervalos entre picos
intervals = np.diff(peaks)
time_between_peaks = intervals / sampling_rate
bpm = 60 / np.mean(time_between_peaks)

print(f"BPM estimado: {bpm:.2f}")
print(f"Número de batimentos detectados: {len(peaks)}")

# Plotar o sinal oscilatório com os picos
plt.figure(figsize=(12, 5))
plt.plot(osc, label='Sinal Oscilatório (batimentos)', color='purple')
plt.plot(peaks, osc[peaks], 'ro', label='Batimentos Detectados')
plt.title('Sinal Oscilatório com Picos')
plt.xlabel('Amostra')
plt.ylabel('Oscilação')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()