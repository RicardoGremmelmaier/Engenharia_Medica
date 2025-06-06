import serial
import time
import csv

# CONFIGURE AQUI:
PORTA_SERIAL = 'COM3'        # ou '/dev/ttyUSB0' no Linux
BAUDRATE = 115200
TEMPO_COLETA = 10            # segundos
ARQUIVO_SAIDA = 'dados.csv'

ser = serial.Serial(PORTA_SERIAL, BAUDRATE, timeout=1)
time.sleep(2)  # Espera ESP32 resetar

print(f"Iniciando coleta por {TEMPO_COLETA} segundos...")
dados = []
inicio = time.time()

while (time.time() - inicio) < TEMPO_COLETA:
    linha = ser.readline().decode('utf-8').strip()
    if linha.isdigit():
        dados.append(int(linha))

ser.close()

# Salvar em CSV
with open(ARQUIVO_SAIDA, 'w', newline='') as f:
    writer = csv.writer(f)
    for valor in dados:
        writer.writerow([valor])

print(f"Coleta finalizada. {len(dados)} amostras salvas em '{ARQUIVO_SAIDA}'.")
