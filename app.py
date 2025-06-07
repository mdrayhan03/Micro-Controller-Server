from flask import Flask, render_template, redirect, url_for, request, jsonify, send_file
from io import BytesIO
from supabase import create_client, Client

class DB :
    def __init__(self):
        url = "https://szvshfwkkuplrnxzdbco.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6dnNoZndra3VwbHJueHpkYmNvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkyODExMDMsImV4cCI6MjA2NDg1NzEwM30.98HqG_clTHdAkqzKYMaT87IB7hVBCSfCYsy20bEM6HM"

        self.base : Client = create_client(url, key)

    def insert_data(self, arr) :
        try :
            data = {
                "temperature" : arr[0],
                "humidity" : arr[1],
                "gas" : arr[2]
            }

            response = self.base.table("Sensor_Data").insert(data).execute()
            return response
        except Exception as e :
            print(f"Insert Error: {e}")
            return None
    
    def select_data(self):
        try:
            response = (
                self.base.table("Sensor_Data")
                .select("*")
                .order("created_at", desc=True)
                .limit(10)
                .execute()
            )
            data = list(response.data)
            return data
        except Exception as e:
            print(f"Select Error: {e}")
            return None

app = Flask(__name__)
db = DB()
latest_image = None

@app.route("/")
def index() :
    arr = db.select_data()
    print(arr)
    return render_template("index.html", data=arr)

@app.route("/home-image")
def home_image():
    return render_template("home_image.html")

@app.route('/post-data', methods=['POST'])
def post_data():
    try:
        # sensor_data = request.form.get('sensor')  # For x-www-form-urlencoded
        sensor_data = request.get_json()  # Uncomment if using JSON

        if not sensor_data:
            return "No data received", 400
        
        if "error" in sensor_data:
            return jsonify({"status": "failed", "message": sensor_data["error"]}), 400

        temperature = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
        gas = sensor_data.get("gas")

        print(f"Temperature: {temperature}({type(temperature)}); Humidity: {humidity}({type(humidity)}); Gas: {gas}({type(gas)})")

        arr = [temperature, humidity, gas]
        db.insert_data(arr)

        return jsonify({"message": "Data received successfully", "data": sensor_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/upload-image', methods=['POST'])
def upload_image():
    global latest_image
    image_bytes = request.data
    if not image_bytes:
        return "No image data received", 400
    latest_image = image_bytes
    return "Image received", 200

@app.route('/latest-image')
def latest_image_view():
    global latest_image
    if latest_image is None:
        return "No image available", 404
    return send_file(BytesIO(latest_image), mimetype='image/jpeg')


# if __name__ == "__main__" :
#     app.run(host='0.0.0.0', port=5000, debug=True)