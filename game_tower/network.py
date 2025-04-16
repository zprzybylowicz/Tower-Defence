import sys
import socket
import threading
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QImage, QFont, QColor
from PyQt5.QtCore import QBuffer, QIODevice


def grab_window(window):
    # Zrzut całego okna
    pixmap = window.grab()
    # Testowy zapis, aby upewnić się, że okno jest uchwycone
    pixmap.save("debug_screenshot.png", "PNG")
    return pixmap.toImage()


def image_to_bytes(image, format='JPEG'):
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, format)
    data = buffer.data()
    buffer.close()
    return data


def client_handler(conn, window):
    try:
        while True:
            image = grab_window(window)
            data = image_to_bytes(image)
            length = len(data)
            conn.sendall(length.to_bytes(4, byteorder='big'))
            conn.sendall(data)
            print(f"[DEBUG] Wysłano klatkę o rozmiarze: {length} bajtów")
            time.sleep(0.2)  #
    except Exception as e:
        print("Błąd podczas wysyłania obrazu:", e)
    finally:
        conn.close()
        print("[DEBUG] Połączenie zakończone.")


def start_image_server(host, port, window):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Serwer streamingu obrazu nasłuchuje na {host}:{port}")
    while True:
        conn, addr = server_socket.accept()
        print("Klient podłączony:", addr)
        threading.Thread(target=client_handler, args=(conn, window), daemon=True).start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Okno Gry - Serwer")
        self.resize(960, 960)

        # Ustawiamy kolor tła
        self.setStyleSheet("background-color: lightblue;")

        # Przykładowe UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        button = QPushButton("Przycisk testowy", self)
        button.setFont(QFont("Arial", 20))
        layout.addWidget(button)

        label = QLabel("To jest okno gry - zawiera przyciski i inne elementy.", self)
        label.setFont(QFont("Arial", 24))
        label.setStyleSheet("color: darkred;")
        layout.addWidget(label)

        # Dodaj jeszcze inny element, np. prostokątny widżet (można dodać przez styl CSS)
        extra_label = QLabel("Extra element", self)
        extra_label.setStyleSheet("background-color: yellow; font-size: 24px;")
        layout.addWidget(extra_label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Opóźnienie o 1000 ms, żeby okno mogło się w pełni wyrenderować
    from PyQt5.QtCore import QTimer

    QTimer.singleShot(1000, lambda: threading.Thread(target=start_image_server, args=('0.0.0.0', 8080, window),
                                                     daemon=True).start())
    sys.exit(app.exec_())
