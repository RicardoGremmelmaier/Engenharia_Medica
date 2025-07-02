import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

file_path = 'dataset/otávioPepe.txt'

# === ETAPA 1: Leitura das duas colunas ===
pressao_bracadeira = []     # Coluna 0: pressão medida na braçadeira 
pressao_oscilatoria = []    # Coluna 1: pressão oscilatória

with open(file_path, 'r') as f:
    for linha in f:
        partes = linha.strip().split(';')
        if len(partes) == 2:
            try:
                p_bra = int(partes[0].strip())
                p_osc = int(partes[1].strip())
                pressao_bracadeira.append(p_bra)
                pressao_oscilatoria.append(p_osc)
            except ValueError:
                continue

# === ETAPA 2: Plot comparativo ===
plt.figure(figsize=(12,5))
plt.plot(pressao_bracadeira, label='Pressão do paciente', color='orange')
plt.plot(pressao_oscilatoria, label='Pressão da braçadeira', color='blue')
plt.legend()
plt.title("Pressão do Paciente vs Braçadeira")
plt.xlabel("Amostra")
plt.ylabel("Valor do Sensor")
plt.grid(True)
plt.tight_layout()
plt.show()


pressao_oscilatoria = np.array(pressao_oscilatoria)
pressao_bracadeira = np.array(pressao_bracadeira)

inicio = 1100

oscilacao_recorte = pressao_oscilatoria[inicio:]
bracadeira_recorte = pressao_bracadeira[inicio:]

picos, _ = find_peaks(oscilacao_recorte, distance=10, prominence=1)

picos_absolutos = picos + inicio

plt.figure(figsize=(12,5))
plt.plot(pressao_bracadeira, label='Pressão do paciente', color='orange')
plt.plot(pressao_oscilatoria, label='Pressão da braçadeira (oscilatória)', color='blue')
plt.plot(picos_absolutos, pressao_oscilatoria[picos_absolutos], 'ro', label='Picos detectados')
plt.legend()
plt.title("Detecção de Picos nas Oscilações (após início da desinflação)")
plt.xlabel("Amostra")
plt.ylabel("Valor do Sensor")
plt.grid(True)
plt.tight_layout()
plt.show()

indice_map = picos_absolutos[np.argmax(pressao_oscilatoria[picos_absolutos])]
valor_map = pressao_oscilatoria[indice_map]
pressao_map = pressao_bracadeira[indice_map]

print(f"MAP detectada: {pressao_map} mmHg (amplitude máxima = {valor_map})")

alvo_sistolica = 0.55 * valor_map
alvo_diastolica = 0.85 * valor_map

picos_antes_map = [i for i in picos_absolutos if i < indice_map]
picos_depois_map = [i for i in picos_absolutos if i > indice_map]

indice_sistolica = min(
    picos_antes_map,
    key=lambda i: abs(pressao_oscilatoria[i] - alvo_sistolica)
)
pressao_sistolica = pressao_bracadeira[indice_sistolica]

indice_diastolica = min(
    picos_depois_map,
    key=lambda i: abs(pressao_oscilatoria[i] - alvo_diastolica)
)
pressao_diastolica = pressao_bracadeira[indice_diastolica]

print(f"Pressão Sistólica estimada: {pressao_sistolica} mmHg (≈ 55% do pico)")
print(f"Pressão Diastólica estimada: {pressao_diastolica} mmHg (≈ 85% do pico)")

plt.figure(figsize=(12,5))
plt.plot(pressao_bracadeira, label='Pressão do paciente', color='orange')
plt.plot(pressao_oscilatoria, label='Oscilação', color='blue')
plt.plot(picos_absolutos, pressao_oscilatoria[picos_absolutos], 'ro', label='Picos detectados')

plt.plot(indice_sistolica, pressao_oscilatoria[indice_sistolica], 'go', label='Sistólica (55%)')
plt.plot(indice_diastolica, pressao_oscilatoria[indice_diastolica], 'mo', label='Diastólica (85%)')
plt.plot(indice_map, pressao_oscilatoria[indice_map], 'ko', label='MAP (100%)')

plt.legend()
plt.title("Cálculo da Pressão Arterial com base nos picos oscilatórios")
plt.xlabel("Amostra")
plt.ylabel("Valor do Sensor")
plt.grid(True)
plt.tight_layout()
plt.show()
