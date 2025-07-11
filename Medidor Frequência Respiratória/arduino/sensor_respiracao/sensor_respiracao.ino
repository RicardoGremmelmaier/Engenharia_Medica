const int sensorPin = A0;
const int numSamples = 10;
int buffer[numSamples];
int index = 0;

unsigned long previousMillis = 0;
const unsigned long interval = 100;  // 100 ms = 10 Hz, 200 ms = 5 Hz, 50 ms = 20 Hz

int threshold = 0;
int maxValue = 0;
int minValue = 1024;           
bool aboveThreshold = false;

const int maxPeaks = 10;
unsigned long times[maxPeaks];
int peaksCounter = 0;

const int redLed = 2;
const int greenLed = 3;

void setup() {
  Serial.begin(9600);
  pinMode(redLed, OUTPUT);
  pinMode(greenLed, OUTPUT);

  digitalWrite(greenLed, HIGH);  // Início da calibração
  calibrateSensor(8000);
  digitalWrite(greenLed, LOW);

  delay(500);
  digitalWrite(redLed, HIGH);  // Calibração concluída
  delay(500);
  digitalWrite(redLed, LOW);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    buffer[index] = analogRead(sensorPin);
    index = (index + 1) % numSamples;

    int sum = 0;
    for (int i = 0; i < numSamples; i++) {
      sum += buffer[i];
    }
    int mean = sum / numSamples;

    if (mean > threshold) {
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
    } else {
      digitalWrite(redLed, LOW);
      digitalWrite(greenLed, HIGH);
    }

    if (mean > threshold && !aboveThreshold) {
      aboveThreshold = true;
      registerPeak(currentMillis);
    } 
    else if (mean < threshold) {aboveThreshold = false;}

    Serial.print(mean); Serial.print(";");
    Serial.println(getRespiratoryRate(currentMillis)); Serial.print(";");
    Serial.print(minValue); Serial.print(";");
    Serial.print(maxValue); Serial.print(";");
    Serial.print(threshold); Serial.print(";");
  }
}

void registerPeak(unsigned long time){
  for (int i = maxPeaks - 1; i > 0; i--){
    times[i] = times[i - 1];
  }
  times[0] = time;
  if (peaksCounter < maxPeaks) {
    peaksCounter++;
  }
}

int getRespiratoryRate(unsigned long currentMillis) {
  if (peaksCounter < 2) {
    return 0;
  }

  unsigned long totalRange = times[0] - times[peaksCounter - 1];
  if (totalRange == 0) return 0;
  
  float seconds = totalRange / 1000.0;
  float rate = (60.0 * (peaksCounter - 1)) / seconds;
  return (int)rate;
}

void calibrateSensor(int duration_ms){
  Serial.println("Calibrando sensor... Respire fundo 3 vezes e aguarde.");

  unsigned long start = millis();
  while (millis() - start < duration_ms){
    int value = analogRead(sensorPin);

    if(value > maxValue) maxValue = value;
    if(value < minValue) minValue = value;
    delay(50);
  }

  threshold = (maxValue + minValue) / 2;
  Serial.print("Valor máximo: ");
  Serial.println(maxValue);
  Serial.print("Valor mínimo: ");
  Serial.println(minValue);
  Serial.print("Valor do limiar: ");
  Serial.println(threshold);
  Serial.println("Calibração concluída.");
}
