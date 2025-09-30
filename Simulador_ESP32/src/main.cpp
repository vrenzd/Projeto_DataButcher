#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "SEU_WIFI";
const char* password = "SUA_SENHA";
const char* servidor = "http://SEU_SERVIDOR:5000/dados";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("WiFi conectado!");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(servidor);
    http.addHeader("Content-Type", "application/json");

    // Simulação dos dados
    String maquina_id = "moedor_001";
    float tensao = random(210, 230); // Voltagem simulada
    int vibracao = random(400, 800); // Vibração simulada
    float temperatura = random(30, 60); // Temperatura simulada
    int rpm = random(1400, 1600); // RPM simulado

    String json = "{";
    json += "\"maquina_id\":\"" + maquina_id + "\",";
    json += "\"tensao\":" + String(tensao, 2) + ",";
    json += "\"vibracao\":" + String(vibracao) + ",";
    json += "\"temperatura\":" + String(temperatura, 2) + ",";
    json += "\"rpm\":" + String(rpm);
    json += "}";

    int resposta = http.POST(json);
    Serial.println("Enviado: " + json);
    Serial.println("Resposta: " + String(resposta));
    http.end();
  }

  delay(5000); // Envia a cada 5 segundos
}
