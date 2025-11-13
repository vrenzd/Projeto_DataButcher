#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";
// Substitua pela sua URL ngrok (copie a https://... e acrescente /dados)
const char* servidor = "https://unseeking-supercritically-carie.ngrok-free.dev/dados";

void setup() {
  Serial.begin(115200);
  delay(100);

  WiFi.begin(ssid, password); // sem especificar canal
  Serial.print("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi conectado, IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure(); // aceita qualquer certificado (só para teste)
    HTTPClient http;

    Serial.println("Iniciando conexão HTTPs...");
    if (http.begin(client, servidor)) {
      http.addHeader("Content-Type", "application/json");

      String maquina_id = "moedor_001";
      float tensao = random(210, 230);
      int vibracao = random(400, 800);
      float temperatura = random(30, 60);
      int rpm = random(1400, 1600);

      String json = "{";
      json += "\"maquina_id\":\"" + maquina_id + "\",";
      json += "\"tensao\":" + String(tensao, 2) + ",";
      json += "\"vibracao\":" + String(vibracao) + ",";
      json += "\"temperatura\":" + String(temperatura, 2) + ",";
      json += "\"rpm\":" + String(rpm);
      json += "}";

      Serial.println("Enviando: " + json);
      int codigo = http.POST(json);

      if (codigo > 0) {
        Serial.printf("Código HTTP: %d\n", codigo);
        String resp = http.getString();
        Serial.println("Resposta servidor: " + resp);
      } else {
        Serial.printf("Erro na requisição. codigo: %d\n", codigo);
      }

      http.end();
    } else {
      Serial.println("Falha no http.begin()");
    }

  } else {
    Serial.println("WiFi desconectado!");
  }

  delay(5000);
}
