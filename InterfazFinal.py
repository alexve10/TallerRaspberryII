from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QPushButton, QDialog, QLabel, QComboBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import QIODevice, Qt, QSize, QTimer
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtGui import QPixmap, QIcon

import sys
import pyqtgraph as pg
import numpy as np


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        loadUi('InterfazTallerV2.ui', self)

        # Establecer fondo
        self.set_background_image('TALLER2.png')

        # Timer grafica
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.graficar)
        self.timer.start(20)

        # Variable Medida
        self.Valor_Med = 0
        self.Valor_LC = 0
        self.Valor_Des = 0.0
        self.Valor_Deseado_Arduino = 0
        self.Val_Tiempo = 100
        self.flag_check_Med = "0"
        self.flag_check_LC = "0"
        self.flag_check_Des = "0"

        # Gráfica
        self.x1 = list(np.linspace(0, self.Val_Tiempo, self.Val_Tiempo))
        self.y1 = list(np.linspace(0, 0, self.Val_Tiempo))
        self.y2 = list(np.linspace(0, 0, self.Val_Tiempo))
        self.y3 = list(np.linspace(0, 0, self.Val_Tiempo))
        self.plt = pg.PlotWidget()
        self.plt.setBackground('w')  # Establecer fondo blanco
        self.plt.showGrid(x=True, y=True)  # Mostrar la cuadrícula
        self.Grafica.addWidget(self.plt)

        # Inicializar combo boxes para puertos y baudrates
        self.cb_list_ports = self.findChild(QComboBox, 'cb_list_ports')
        self.cb_list_baudrates = self.findChild(QComboBox, 'cb_list_baudrates')

        self.Bot_Enviar.clicked.connect(self.EnviarValores)
        self.Bot_Enviar.setStyleSheet("background-color: #bb1042;")
        self.Val_Deseado.valueChanged.connect(self.valor_cambiado)

        self.serial = QSerialPort()
        self.serial.readyRead.connect(self.read_data)
        self.Actualizar.clicked.connect(self.read_ports)
        self.Conectar.clicked.connect(self.serial_connect)
        self.Desconectar.clicked.connect(lambda: self.serial.close())

        # Checkboxes
        self.Check_Med.toggled.connect(self.check_toggle)
        self.Check_Des.toggled.connect(self.check_toggle)
        self.Check_LC.toggled.connect(self.check_toggle)

        # Leer puertos al inicio
        self.read_ports()
        
    def set_background_image(self, image_path):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-image: url({image_path});
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
        """)

    def valor_cambiado(self, value):
        self.Valor_Des = value
        print(self.Valor_Des)

    def check_toggle(self):
        if self.Check_Med.isChecked():
            self.flag_check_Med = "1"
        else:
            self.flag_check_Med = "0"

        if self.Check_Des.isChecked():
            self.flag_check_Des = "1"
        else:
            self.flag_check_Des = "0"

        if self.Check_LC.isChecked():
            self.flag_check_LC = "1"
        else:
            self.flag_check_LC = "0"

    def EnviarValores(self):
        data = str(self.Valor_Des) + "\n"
        print(data)

        if self.serial.isOpen():
            self.serial.write(data.encode())

    def read_ports(self):
        self.baudrates = ['1200', '2400', '4800', '9600', '19200', '38400', '115200']

        portlist = []
        ports = QSerialPortInfo().availablePorts()
        for i in ports:
            portlist.append(i.portName())

        self.cb_list_ports.clear()
        self.cb_list_baudrates.clear()
        self.cb_list_ports.addItems(portlist)
        self.cb_list_baudrates.addItems(self.baudrates)
        self.cb_list_baudrates.setCurrentText('9600')

    def serial_connect(self):
        self.port = self.cb_list_ports.currentText()
        self.baud = self.cb_list_baudrates.currentText()
        self.serial.setBaudRate(int(self.baud))
        self.serial.setPortName(self.port)
        if self.serial.open(QIODevice.OpenModeFlag.ReadWrite):
            print(f"Connected to port {self.port} with baudrate {self.baud}")
        else:
            print(f"Failed to connect to port {self.port}")

    def read_data(self):
        if not self.serial.canReadLine():
            return

        rx = self.serial.readLine()
        rx = str(rx, 'utf-8').strip()
        print(rx)

        # Dividir los datos en una lista
        data_list = rx.split(',')

        if len(data_list) != 3:
            return

        # Convertir los valores a números flotantes
        y1, y2, y3 = map(float, data_list)

        self.Valor_Deseado_Arduino = y1
        self.Valor_Med = y2
        self.Valor_LC = y3

    def graficar(self):
        plot_colors = ['#FF0000', '#0019FF', '#A2FF00']

        plots = []
        self.y1 = self.y1[1:]
        self.y1.append(self.Valor_Med)  # Graficar el 1 valor
        self.y2 = self.y2[1:]
        self.y2.append(self.Valor_Deseado_Arduino)  # Graficar el 2 valor
        self.y3 = self.y3[1:]
        self.y3.append(self.Valor_LC)  # Graficar el 3 valor

        self.y_values = [self.y1, self.y2, self.y3]
        checkbox_flags = [self.flag_check_Med, self.flag_check_Des, self.flag_check_LC]
        legend_names = ["Val 1", "Val 2", "Val 3"]

        self.plt.clear()

        for i in range(len(legend_names)):
            if checkbox_flags[i] == "1":
                self.plt.plot(self.x1, self.y_values[i], pen=pg.mkPen(plot_colors[i], width=4), name=legend_names[i])
                plots.append(i)

        if not plots:
            self.plt.clear()
        
        self.actualizar_valores()

    def actualizar_valores(self):
        Valor_Medido = str(self.Valor_Med)
        self.Val_Med.setText(Valor_Medido)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec())
