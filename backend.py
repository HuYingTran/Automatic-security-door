from flask import Flask, Response, render_template, jsonify, request
import sqlite3
import threading
import time
from camera import detect_motion, generate, controll_camera
from flask_socketio import SocketIO
from threading import Event

global t
data_sql = None

camera_thread = None
camera_status = "off"
stop_event = Event()

app = Flask(__name__)
socketio = SocketIO(app)

# Hàm truy vấn cơ sở dữ liệu để lấy trạng thái các cảm biến
def get_sensor_status():
    connection = sqlite3.connect('raspberrypi.db')  # Đường dẫn đến cơ sở dữ liệu SQLite
    cursor = connection.cursor()
    cursor.execute('SELECT sensor_name, status FROM sensor_status')
    rows = cursor.fetchall()
    connection.close()
    return rows

def data_thread():
    while True:
        global data_sql
        if not data_sql :
            time.sleep(2)
        data_current = get_sensor_status() # Lấy giá trị khởi tạo từ DB
        if data_sql != data_current:
            if socketio.server.eio.sockets: # Kiểm tra có client đang kết nối
                socketio.emit('update_sensor_status', {'sensor_statuses': data_current})
                print('Update data to Web')
                data_sql = data_current
        time.sleep(1)

@app.route('/')
def index():
    global data_sql
    data_sql = None
    camera_status = "off"
    sensor_statuses = get_sensor_status()  # Lấy danh sách trạng thái cảm biến từ cơ sở dữ liệu
    return render_template('index.html', sensor_statuses=sensor_statuses)

@app.route('/camera_stream')
def camera_stream():
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/api', methods=['GET'])
def api():
    global camera_thread, camera_status, stop_event
    # Lấy tham số 'status' từ URL
    status = request.args.get('camera_status')
    print(f"Camera status requested: {status}")
    if status == 'on' and camera_status == "off":
        stop_event.clear()
        controll_camera(status)
        camera_status = "on"  # Đặt trạng thái của camera là 'on'
        camera_thread = threading.Thread(target=detect_motion, args=(10,stop_event))
        camera_thread.daemon = True
        camera_thread.start()
        return jsonify({"Sucessfull": "Camera turned on"}), 200
    elif status == 'off' and camera_status == 'on':
        stop_event.set()  # Báo hiệu dừng thread
        camera_thread.join()  # Đợi thread kết thúc
        controll_camera(status)
        camera_status = "off"  # Đặt trạng thái của camera là 'off'
        return jsonify({"Sucessfull": "Camera turned off"}), 200
    else:
        # Nếu tham số 'status' không hợp lệ
        return jsonify({"error": "Invalid status parameter"}), 400

if __name__ == '__main__':
    thread = threading.Thread(target=data_thread)
    thread.daemon = True  # Đảm bảo thread tự tắt khi Flask app tắt
    thread.start()

    socketio.run(app, debug=True, host='0.0.0.0', port='5000')
