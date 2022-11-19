from PyQt5.QtWidgets import QProgressBar, QLabel, QTextBrowser, QFrame
from PyQt5 import uic, QtCore, QtTest, QtGui
import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox
from PyQt5.QtCore import QTimer, Qt
import json
from backend import get_data, get_row
from data.StartingUI import Ui_MainWindow

TEXT_ORDER = get_data()


class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # SETTING UP UI
        self.setupUi(self)
        self.setWindowTitle('Typing Test')
        self.setWindowIcon(QtGui.QIcon('Icon.ico'))
        self.statistics = QMessageBox()
        # SETTING UP ADDITIONAL VARIABLES
        self.started = False
        self.texts = get_data()
        self.text_number = 0
        # STARTING THE TIMER
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_speed)
        self.timer.start(1000)
        self.run()

    # WRITES DOWN PARAMS AS A NEW RECORD
    def set_new_record(self, speed, accuracy):
        with open("data/record.json", 'r+') as save:
            copy_save = json.load(save)
            copy_save['best_speed'] = max(float(copy_save['best_speed']), float(speed))
            copy_save['best_accuracy'] = max(float(copy_save['best_accuracy']), float(accuracy))
            copy_save['avg_speed'].append(float(speed))
            copy_save['avg_accuracy'].append(float(accuracy))
        with open('data/record.json', 'w') as openfile:
            json.dump(copy_save, openfile)

    # FUNCTION THAT CHECKS IF CLICKED BUTTON(-S) ARE SAME WITH A CHARACTER
    def check_instance(self, event, goal: str):
        if goal.isalpha() and goal.isupper() and event.key() == ord(goal):
            if int(event.modifiers()) == Qt.ShiftModifier:
                return True
            else:
                return False
        elif goal.isalpha() and goal.islower() and event.key() == ord(goal.upper()):
            if int(event.modifiers()) != Qt.ShiftModifier:
                return True
            else:
                return False
        elif goal == ' ' and event.key() == Qt.Key_Space:
            return True
        elif event.key() == ord(goal):
            return True
        else:
            return False

    # THIS FUNCTION IS BEING PERIODICALLY CALLED TO UPDATE SPEED THAT SHOWS TO THE USER
    def check_speed(self):
        if self.started:
            try:
                self.speed.setText(
                    str(round(self.progress_done / int(time.time() - self.time_started) * 60, 2)))
                self.update_ui()
            except ZeroDivisionError:
                self.speed.setText('0')

    # THIS FUNCTION BASICALLY DOES ALL THE HARD WORK WITH EVENTS
    def keyPressEvent(self, event):
        if not self.started:
            self.started = True
            self.time_started = time.time()

        if self.check_instance(event, self.text[self.progress_done]):
            if not self.wrong:
                self.progress_done += 1
                self.progress_remain += 1
                self.update_ui()
            else:
                self.done = self.done + self.wrong
                self.wrong = ''
                self.progress_done += 1
                self.update_ui()
        elif event.key() == Qt.Key_Shift:
            pass
        else:
            if not self.wrong:
                self.progress_remain += 1
                self.wrong = self.text[self.progress_done]
                self.mistakes.setText(str(int(self.mistakes.text()) + 1))
                self.update_ui()
            else:
                self.wrong = self.text[self.progress_done]
                self.update_ui()
        if self.done == self.text:
            accuracy = int(round(1 - int(self.mistakes.text()) /
                                 len(self.text.split(' ')), 2) * 100)
            self.set_new_record(self.speed.text(), accuracy)
            self.started = False
            QMessageBox.about(self, 'Results',
                              f'You\'ve done {self.mistakes.text()} mistakes of an average speed of'
                              f' {self.speed.text()}ch/min and accuracy of '
                              f'{accuracy}'
                              f' %')

            self.run()

    # THIS FUNCTION RESETS UI TO 'STARTING' POSITION, IT IS CALLED WHEN A USER WRITES ONE TEXT AND
    # WANT'S ANOTHER
    def run(self):
        self.text = get_row(TEXT_ORDER[self.text_number])[0]
        self.text_number += 1
        self.progress_done = 0  # Прогресс сделанных
        self.progress_remain = 0  # Прогресс оставшихся
        self.done = self.text[:self.progress_done]  # Сделанный текст
        self.wrong = ''  # Ошибочный
        self.undone = self.text[self.progress_remain:]  # Не сделанный текст
        self.textInterface.setHtml(f'<span style="color:#989898;">{self.done}</span>'
                                   f'<span style="color:#d70007;">{self.wrong}</span>'
                                   f'<span style="color:#ffffff;">{self.undone}</span>')
        self.time_bar.setMaximum(len(self.text))
        self.time_bar.setMinimum(0)
        self.time_bar.setValue(self.progress_done)
        with open("data/record.json", 'r+') as openfile:
            s = json.load(openfile)
            try:
                self.record.setText(f'{round(sum(s["avg_speed"]) / len(s["avg_speed"]), 1)}'
                                    f'ch/min '
                                    f'{round(sum(s["avg_accuracy"]) /len(s["avg_accuracy"]), 1)}%')
            except ZeroDivisionError:
                self.record.setText(f'0 ch/min none%')
        self.mistakes.setText('0')
        self.speed.setText('0')

    # THIS FUNCTION UPDATES (DOESN'T RESET) THE UI
    def update_ui(self):
        self.done = self.text[:self.progress_done]  # Сделанный текст
        self.undone = self.text[self.progress_remain:]  # Не сделанный текст
        self.textInterface.setHtml(f'<span style="color:#989898;">{self.done}</span>'
                                   f'<span style="color:#d70007;">{self.wrong}</span>'
                                   f'<span style="color:#ffffff;">{self.undone}</span>')
        self.time_bar.setMaximum(len(self.text))
        self.time_bar.setMinimum(0)
        self.time_bar.setValue(self.progress_done)
        with open("data/record.json", 'r+') as openfile:
            s = json.load(openfile)
            try:
                self.record.setText(f'{round(sum(s["avg_speed"]) / len(s["avg_speed"]), 1)}'
                                    f'ch/min '
                                    f'{round(sum(s["avg_accuracy"]) /len(s["avg_accuracy"]), 1)}%')
            except ZeroDivisionError:
                self.record.setText(f'0 ch/min none%')


# BASICALLY DOES THAT WHEN PROGRAM IS FACING SOME UNEXPECTED ERRORS, IT WON'T CRUSH
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# MAIN LOOP
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    ex.setFocus()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
