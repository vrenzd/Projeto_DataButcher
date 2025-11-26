#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h> // Essencial para analisar o JSON recebido
#include <HTTPClient.h>  // Para a função de enviar dados

// ===============================
// CONFIGURAÇÕES
// ===============================
const char* SSID = "Wokwi-GUEST";
const char* PASSWORD = "";

// --- MQTT ---
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MAQUINA_ID = "691c604dd1819b43462cf57a"; // Use o ID real da sua máquina

// --- API ---
const String SENSOR_DATA_URL = "https://mailed-hills-conditioning-thesis.trycloudflare.com/api/sensor-data";

// ===============================
// VARIÁVEIS GLOBAIS
// ===============================
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient );

// --- A MÁQUINA DE ESTADOS ---
bool maquinaIniciada = false; // Começa como 'parada'
unsigned long ultimoEnvio = 0;
const long intervaloEnvio = 5000; // Enviar dados a cada 5 segundos

// ===============================
// FUNÇÕES
// ===============================

// Função para enviar dados (você já tem essa)
void enviarDados() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(SENSOR_DATA_URL ); // Use WiFiClientSecure se seu túnel for HTTPS
  http.addHeader("Content-Type", "application/json" );

  // Monta o JSON para enviar
  String payload = "{\"maquina_id\":\"" + String(MAQUINA_ID) + "\",\"tensao\":225.5,\"vibracao\":2.1,\"temperatura\":65.3,\"rpm\":1500}";
  
  Serial.println("Enviando dados do sensor...");
  int httpCode = http.POST(payload );

  if (httpCode > 0 ) {
    Serial.printf("Dados enviados, código de resposta: %d\n", httpCode );
  } else {
    Serial.printf("Falha ao enviar dados, erro: %s\n", http.errorToString(httpCode ).c_str());
  }
  http.end( );
}


// --- CALLBACK DO MQTT: O CÉREBRO DA LÓGICA ---
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensagem recebida no tópico: ");
  Serial.println(topic);

  // Analisa o JSON recebido de forma segura
  JsonDocument doc; // Use a biblioteca ArduinoJson
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.print("Falha ao analisar JSON: ");
    Serial.println(error.c_str());
    return;
  }

  // Extrai o comando do JSON
  const char* comando = doc["comando"]; // Ex: "start", "stop"

  if (comando) { // Verifica se a chave "comando" existe
    if (strcmp(comando, "start") == 0) {
      Serial.println("Comando 'start' recebido! Iniciando a máquina.");
      maquinaIniciada = true;

      // Opcional: Extrair parâmetros
      float velocidade = doc["parametros"]["velocidade"];
      Serial.printf("Velocidade definida para: %.2f RPM\n", velocidade);
      // Aqui você ajustaria os pinos do motor, etc.

    } else if (strcmp(comando, "stop") == 0) {
      Serial.println("Comando 'stop' recebido! Parando a máquina.");
      maquinaIniciada = false;
    }
  }
}

// Função para conectar/reconectar ao MQTT
void reconectarMqtt() {
  while (!mqttClient.connected()) {
    Serial.print("Tentando conectar ao Broker MQTT...");
    if (mqttClient.connect("ESP32_DATABUTCHER_CLIENT")) {
      Serial.println("Conectado!");
      String topic = "maquinas/" + String(MAQUINA_ID) + "/comandos";
      mqttClient.subscribe(topic.c_str());
      Serial.print("Subscrito ao tópico: ");
      Serial.println(topic);
    } else {
      Serial.print("falhou, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

// Conexão WiFi
void conectarWiFi() {
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
}

// ===============================
// SETUP E LOOP PRINCIPAL
// ===============================
void setup() {
  Serial.begin(115200);
  conectarWiFi();
  
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(callback);
}

void loop() {
  // Garante que a conexão MQTT esteja sempre ativa
  if (!mqttClient.connected()) {
    reconectarMqtt();
  }
  mqttClient.loop(); // ESSENCIAL: Processa mensagens recebidas

  // --- LÓGICA PRINCIPAL CONDICIONADA PELO ESTADO ---
  if (maquinaIniciada) {
    // A máquina está ligada, então vamos enviar os dados periodicamente
    unsigned long agora = millis();
    if (agora - ultimoEnvio >= intervaloEnvio) {
      ultimoEnvio = agora; // Reseta o temporizador
      enviarDados();
    }
  } else {
    // A máquina está parada. Não fazemos nada, apenas esperamos por comandos.
    // Você poderia piscar um LED aqui para indicar o modo "standby".
    delay(100); // Pequeno delay para não sobrecarregar o loop
  }
}