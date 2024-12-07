import time
import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_vl53l0x import VL53L0X

tof_status = [0,0,0,0,0,0]

# Khởi tạo I2C
i2c = board.I2C()  # sử dụng board.SCL và board.SDA

# Chân XSHUT kết nối với các cảm biến VL53L0X
xshut = [
    DigitalInOut(board.D7),
    DigitalInOut(board.D9),
    DigitalInOut(board.D10),
]

vl53 = []

def pir_setup():
    # Khởi tạo các nút bấm (buttons)
    pir_1 = DigitalInOut(board.D4)  # Nút bấm 1
    pir_1.direction = Direction.INPUT
    pir_1.pull = Pull.UP  # Kéo lên, khi không nhấn là HIGH

    pir_2 = DigitalInOut(board.D5)  # Nút bấm 2
    pir_2.direction = Direction.INPUT
    pir_2.pull = Pull.UP  # Kéo lên, khi không nhấn là HIGH

def tof_setup():
    # Tắt cảm biến trước khi thay đổi địa chỉ
    for power_pin in xshut:
        power_pin.switch_to_output(value=False)

    # Giới thiệu cảm biến và thay đổi địa chỉ I2C cho mỗi cảm biến
    for i, power_pin in enumerate(xshut):
        power_pin.value = True  # Kích hoạt cảm biến
        time.sleep(0.1)  # Chờ để cảm biến khởi động

        # Thêm cảm biến vào danh sách
        vl53.append(VL53L0X(i2c))

        if i < len(xshut) - 1:
            vl53[i].set_address(i + 0x30)  # Đảm bảo địa chỉ là duy nhất


def detect_range():
    while True:
        global tof_status, vl53
        tof_status_n = [0,0,0,0,0,0]
        tof_status_n[1] = 1 if not button1.value else 0
        tof_status_n[2] = 1 if not button2.value else 0

        if tof_status_n[1] or tof_status_n[2]:
            tof_status_n[0] = 1
            print('ON Cam by GPIO')

        # Đọc và in ra giá trị khoảng cách từ các cảm biến VL53L0X
        for index, sensor in enumerate(vl53):
            if sensor.range < max_range:
                tof_status_n[index+3] = 1
        if tof_status != tof_status_n:
            tof_status = tof_status_n
            set_sensor_status(tof_status)
            print('Update SQL')

def set_sensor_status(status):
    conn = sqlite3.connect("raspberrypi.db")
    cursor = conn.cursor()
    print(status)
    # Cập nhật trạng thái vào bảng
    for idx, status in enumerate(statuses, start=1):  # start=1 để id bắt đầu từ 1
        cursor.execute("UPDATE sensor_status SET status = ? WHERE id = ?", (status, idx))
    # Lưu thay đổi vào cơ sở dữ liệu
    conn.commit()