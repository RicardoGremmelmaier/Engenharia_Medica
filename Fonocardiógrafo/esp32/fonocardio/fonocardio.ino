const int adcPin = 36;  // GPIO36 (ADC1_CHANNEL_0)
const int bufferSize = 1024;
volatile uint16_t sampleBuffer[bufferSize];
volatile int writeIndex = 0;
volatile int readIndex = 0;


hw_timer_t *timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

volatile uint16_t lastSample = 0;const int adcPin = 36;  // GPIO36
const int bufferSize = 1024;
volatile uint16_t sampleBuffer[bufferSize];
volatile int writeIndex = 0;
volatile int readIndex = 0;

const int samplesPerBatch = 512; // Quantas amostras enviar por vez

hw_timer_t *timer = NULL;
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);

  uint16_t val = analogRead(adcPin);
  sampleBuffer[writeIndex] = val;
  writeIndex = (writeIndex + 1) % bufferSize;

  // Se o buffer encher, sobrescreve o mais antigo
  if (writeIndex == readIndex) {
    readIndex = (readIndex + 1) % bufferSize;
  }

  portEXIT_CRITICAL_ISR(&timerMux);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetAttenuation(ADC_0db);

  timer = timerBegin(0, 80, true);        // 1 µs por tick
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 666, true);      // 666 µs = 1.5 kHz
  timerAlarmEnable(timer);
}

void loop() {
  static uint16_t localBuffer[samplesPerBatch];
  int count = 0;

  // Copiar dados do buffer circular para um buffer local
  portENTER_CRITICAL(&timerMux);
  while (readIndex != writeIndex && count < samplesPerBatch) {
    localBuffer[count++] = sampleBuffer[readIndex];
    readIndex = (readIndex + 1) % bufferSize;
  }
  portEXIT_CRITICAL(&timerMux);

  // Enviar os dados via UART
  for (int i = 0; i < count; i++) {
    Serial.println(localBuffer[i]);
  }

  // Pequena pausa para não sobrecarregar a serial
  delay(1);
}


void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // 12 bits (0–4095)
  analogSetAttenuation(ADC_0db); // Sem atenuação (0–1V ideal)

  // Configura timer: 80 MHz / 80 = 1 MHz → 1 tick = 1 µs
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &onTimer, true);
  timerAlarmWrite(timer, 666, true);  // 666 µs = 1.5 kHz
  timerAlarmEnable(timer);
}

void IRAM_ATTR onTimer() {
  portENTER_CRITICAL_ISR(&timerMux);

  uint16_t val = analogRead(adcPin);
  sampleBuffer[writeIndex] = val;
  writeIndex = (writeIndex + 1) % bufferSize;

  // (Opcional) evitar sobrescrever dados não lidos:
  if (writeIndex == readIndex) {
    readIndex = (readIndex + 1) % bufferSize;  // sobrescreve o mais antigo
  }

  portEXIT_CRITICAL_ISR(&timerMux);
}


void loop() {
  int localReadIndex;

  // Ler dados do buffer
  while (true) {
    portENTER_CRITICAL(&timerMux);
    if (readIndex == writeIndex) {
      portEXIT_CRITICAL(&timerMux);
      break;  // Nada novo
    }

    uint16_t sample = sampleBuffer[readIndex];
    readIndex = (readIndex + 1) % bufferSize;
    portEXIT_CRITICAL(&timerMux);

    // Processar ou imprimir a amostra
    Serial.println(sample);  // Pode ser substituído por transmissão, etc.
  }

  // Esperar um pouco para não travar o Serial
  delay(1);
}



