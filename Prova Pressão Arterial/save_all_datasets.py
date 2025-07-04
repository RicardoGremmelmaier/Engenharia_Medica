import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.signal import find_peaks


def salvar_plot(fig, caminho_completo, dpi=300):
    pasta = os.path.dirname(caminho_completo)
    os.makedirs(pasta, exist_ok=True)
    fig.savefig(caminho_completo, dpi=dpi, bbox_inches='tight')
    print(f"Figura salva em: {caminho_completo}")

dataset_dir = 'dataset/'

for file_name in os.listdir(dataset_dir):
    if not file_name.endswith('.txt'):
        continue

    file_path = os.path.join(dataset_dir, file_name)
    user_name = file_name.split('.')[0]

    print(f"Processando arquivo: {file_name}")

    pressao_bracadeira = []    
    pressao_oscilatoria = []    

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

    if not pressao_bracadeira or not pressao_oscilatoria:
        print(f"Dados vazios ou inválidos em {file_name}")
        continue

    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(pressao_bracadeira, label='Pressão da braçadeira', color='orange')
    ax.plot(pressao_oscilatoria, label='Pressão do paciente (oscilatória)', color='blue')
    ax.legend()
    ax.set_title("Pressão do Paciente vs Braçadeira")
    ax.set_xlabel("Amostra")
    ax.set_ylabel("Valor do Sensor")
    ax.grid(True)
    fig.tight_layout()

    salvar_plot(fig, f'results/imagens/{user_name}/pressao_vs_bracadeira.png')
    plt.close(fig)


    pressao_oscilatoria = np.array(pressao_oscilatoria)
    pressao_bracadeira = np.array(pressao_bracadeira)

    inicio = 1100

    oscilacao_recorte = pressao_oscilatoria[inicio:]
    bracadeira_recorte = pressao_bracadeira[inicio:]

    picos, _ = find_peaks(oscilacao_recorte, distance=10, prominence=1)

    picos_absolutos = picos + inicio

    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(pressao_bracadeira, label='Pressão da braçadeira', color='orange')
    ax.plot(pressao_oscilatoria, label='Pressão do paciente (oscilatória)', color='blue')
    ax.plot(picos_absolutos, pressao_oscilatoria[picos_absolutos], 'ro', label='Picos detectados')
    ax.legend()
    ax.set_title("Detecção de Picos nas Oscilações (após início da desinflação)")
    ax.set_xlabel("Amostra")
    ax.set_ylabel("Valor do Sensor")
    ax.grid(True)
    fig.tight_layout()

    salvar_plot(fig, f'results/imagens/{user_name}/detecao_picos_oscilatorios.png')
    plt.close(fig)

    indice_map = picos_absolutos[np.argmax(pressao_oscilatoria[picos_absolutos])]
    valor_map = pressao_oscilatoria[indice_map]
    pressao_map = pressao_bracadeira[indice_map]


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


    fig, ax = plt.subplots(figsize=(12,5))
    ax.plot(pressao_bracadeira, label='Pressão da braçadeira', color='orange')
    ax.plot(pressao_oscilatoria, label='Pressão oscilatória', color='blue')

    ax.plot(indice_sistolica, pressao_oscilatoria[indice_sistolica], 'go', label='Sistólica (55%)')
    ax.plot(indice_diastolica, pressao_oscilatoria[indice_diastolica], 'mo', label='Diastólica (85%)')
    ax.plot(indice_map, pressao_oscilatoria[indice_map], 'ko', label='MAP (100%)')

    ax.legend()
    ax.set_title("Cálculo da Pressão Arterial com base nos picos oscilatórios")
    ax.set_xlabel("Amostra")
    ax.set_ylabel("Valor do Sensor")
    ax.grid(True)
    fig.tight_layout()

    salvar_plot(fig, f'results/imagens/{user_name}/calculo_pressao_arterial.png')
    plt.close(fig) 

    with open('results/resultados.txt', 'a') as f_resultado:
        f_resultado.write(f"{user_name}: {pressao_sistolica}/{pressao_diastolica}\n")
