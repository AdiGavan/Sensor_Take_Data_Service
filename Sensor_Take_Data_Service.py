from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

db = None

@app.before_first_request
def before_first_request_func():

    global db
    db = psycopg2.connect(host='db_sensors', port=5432, user='postgres', password='postgres', dbname='sensors_info_db')
    #db = psycopg2.connect("postgresql+psycopg2://postgres:postgres@db:5432/example")
    #db = psycopg2.connect(user='postgres', password='postgres', dbname='sensors_info_db')

    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE if not exists sensors_values (
                id SERIAL PRIMARY KEY,
                sensor_type VARCHAR(20) NOT NULL,
                sensor_date DATE NOT NULL,
                sensor_time TIME NOT NULL,
                sensor_value NUMERIC (12, 6) NOT NULL

        )
        """)
    cursor.close()
    db.commit()
    if db is not None:
        db.close()

# Function for adding new line into the database
def addDataToDatabase(sensorType, sensorDate, sensorTime, sensorValue):
    global db
    db = psycopg2.connect(host='db_sensors', port=5432, user='postgres', password='postgres', dbname='sensors_info_db')
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO sensors_values(sensor_type, sensor_date, sensor_time, sensor_value) VALUES(%s, %s, %s, %s) RETURNING id", (sensorType, sensorDate, sensorTime, sensorValue))
        lineID = cursor.fetchone()[0]
        db.commit()
    except:
        lineID = -1

    if cursor is not None:
        cursor.close()
    if db is not None:
        db.close()

    return lineID


@app.route('/', methods=['POST'])
def take_data():
    
    jsonData = request.get_json()
    sensorType = jsonData['sensortype']
    sensorDate = jsonData['sensordate']
    sensorTime = jsonData['sensortime']
    sensorValue = jsonData['sensorvalue']
    lineID = addDataToDatabase(sensorType, sensorDate, sensorTime, sensorValue)

    # Test (returneaza datele introduse + id-ul)
    #return jsonify({'result' : 'Success!', 'Type' : sensorType, 'Date' : sensorDate, "Time" : sensorTime, "Value" : sensorValue, "ID" : lineID})
    
    if lineID == -1:
        status = "Failed"
        error = "Error at adding the line in the database."

    else:
        status = "Success"
        error = "Nothing"

    return jsonify({"status" : status, "error" : error})

if __name__ == "__main__":
    app.run(host="0.0.0.0")