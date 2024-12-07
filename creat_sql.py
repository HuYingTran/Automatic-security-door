import sqlite3

# Kết nối đến cơ sở dữ liệu SQLite (nếu tệp không tồn tại, nó sẽ được tạo ra)
connection = sqlite3.connect('security.db')

# Tạo đối tượng cursor để thực thi các câu lệnh SQL
cursor = connection.cursor()

# Tạo bảng sensor_status nếu bảng chưa tồn tại
cursor.execute('''
CREATE TABLE IF NOT EXISTS sensor_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_name TEXT NOT NULL,
    status INTEGER NOT NULL
);
''')

# Commit các thay đổi và đóng kết nối
connection.commit()

# Đóng kết nối
connection.close()

print("Cơ sở dữ liệu và bảng đã được tạo thành công!")
