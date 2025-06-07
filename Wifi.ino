#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

// DHT11 sensor
#define DHTPIN D1
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "Cudy-Guest-2.4G";
const char* password = "testwifi";

const char* serverUrl = "http://192.168.9.127:5000/post-data";  // Replace with your PC's IP

WiFiClient client;  // Required for HTTPClient in newer API

// void wifi_connection() {
//   Serial.println("Connecting to WiFi...");
//   while (WiFi.status() != WL_CONNECTED) {
//     delay(1000);
//     Serial.print(".");
//   }
//   Serial.println("\nConnected to WiFi!");
// }

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Read sensors
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    int gas = analogRead(A0);

    String postData;

    if (!isnan(t) && !isnan(h)) {
      postData = "{\"temperature\": " + String(t, 2) + 
                 ", \"humidity\": " + String(h, 2) + 
                 ", \"gas\": " + String(gas) + "}";
    } else {
      postData = "{\"error\": \"Sensor data is not reading.\"}";
    }

    int httpCode = http.POST(postData);
    Serial.print("HTTP Code: ");
    Serial.print(httpCode);
    Serial.print("; Response: ");
    Serial.println(http.getString());

    if (httpCode > 0) {
      String response = http.getString();
      Serial.println("Server Response: " + response);
    } else {
      Serial.printf("POST failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }

  Serial.println("Going to deep sleep for 3 minutes...");
  ESP.deepSleep(180e6);  // 180,000,000 microseconds = 3 minutes
}

void loop() {
  // Nothing needed here because ESP will sleep after setup()
}