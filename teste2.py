# from PyQt6.QtWidgets import QApplication, QMainWindow, QCalendarWidget, QLabel, QVBoxLayout, QWidget
# from PyQt6.QtCore import QDate

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.calendar = QCalendarWidget()
#         self.label = QLabel("Selecione uma data no calendário")

#         self.calendar.selectionChanged.connect(self.data_selecionada)

#         layout = QVBoxLayout()
#         layout.addWidget(self.calendar)
#         layout.addWidget(self.label)

#         container = QWidget()
#         container.setLayout(layout)

#         self.setCentralWidget(container)

#     def data_selecionada(self):
#         data = self.calendar.selectedDate()
#         self.label.setText(f"Data selecionada: {data.toString('dd/MM/yyyy')}")
#         print(data.toString('dd/MM/yyyy'))

# app = QApplication([])
# window = MainWindow()
# window.show()
# app.exec()


from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTimeEdit, QLabel
from PyQt6.QtCore import QTime

class Janela(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Input de Horário")

        layout = QVBoxLayout()

        self.time_edit = QTimeEdit()
        # self.time_edit.setTime(QTime.currentTime())  # define o horário atual
        self.time_edit.timeChanged.connect(self.atualizar_horario)

        self.label = QLabel("Horário selecionado:")

        layout.addWidget(self.time_edit)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def atualizar_horario(self, time):
        self.label.setText(f"Horário selecionado: {time.toString('HH:mm')}")

app = QApplication([])
janela = Janela()
janela.show()
app.exec() 