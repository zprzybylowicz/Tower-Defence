import socket
import struct
import sys
import threading
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG

def recvall(conn, count):
    buf = b''
    while count:
        newbuf = conn.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def receive_image(conn):
    raw_length = recvall(conn, 4)
    if not raw_length:
        return None
    length = int.from_bytes(raw_length, byteorder='big')
    print(f"[DEBUG] Otrzymano długość obrazu: {length} bajtów")
    data = recvall(conn, length)
    if not data:
        return None
    image = QImage()
    if not image.loadFromData(data):
        print("[DEBUG] Nie udało się załadować obrazu")
    return image

def start_image_client(host, port, label):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except Exception as e:
        print("Błąd połączenia:", e)
        return

    try:
        while True:
            image = receive_image(client_socket)
            if image is not None:
                pixmap = QPixmap.fromImage(image)
                print(f"[DEBUG] Otrzymano obraz o rozmiarze: {pixmap.size()}")
                # Używamy QMetaObject.invokeMethod, aby ustawić pixmap w głównym wątku GUI
                QMetaObject.invokeMethod(label, "setPixmap", Qt.QueuedConnection, Q_ARG(QPixmap, pixmap))
                # Opcjonalnie możesz dodać: label.update() lub label.repaint() w osobnym invokeMethod
            else:
                print("[DEBUG] Otrzymano pusty obraz")
    except Exception as e:
        print("Błąd podczas odbierania obrazu:", e)
    finally:
        client_socket.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    label = QLabel("Ładowanie streama...")
    label.setAlignment(Qt.AlignCenter)
    label.resize(960, 960)
    label.setScaledContents(True)
    label.show()

    # Upewnij się, że adres IP odpowiada maszynie serwera (np. '192.168.0.178')
    threading.Thread(target=start_image_client, args=('172.20.10.5', 8080, label), daemon=True).start()

    sys.exit(app.exec_())
