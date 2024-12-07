import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QStandardPaths
import os

class LoginWindow(QWidget):  # Окно для авторизации
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Авторизация')
        self.setGeometry(600, 175, 400, 300)
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        self.setPalette(palette)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label = QLabel(
            '<h1 style="color: #FFA500; font-weight: bold; text-align: center;">Добро пожаловать</h1>')
        layout.addWidget(title_label)

        self.username_label = QLabel('Логин:')
        self.username_label.setStyleSheet("font-size: 15px; font-family: Arial, sans-serif; color: #333333;")
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите ваш логин")
        self.username_input.setStyleSheet(
            "padding: 12px; font-size: 16px; border: 2px solid #FFA500; border-radius: 5px;")
        self.username_input.textChanged.connect(self.update_button_state)

        self.password_label = QLabel('Пароль:')
        self.password_label.setStyleSheet("font-size: 15px; font-family: Arial, sans-serif; color: #333333;")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setStyleSheet(
            "padding: 12px; font-size: 16px; border: 2px solid #FFA500; border-radius: 5px;")
        self.password_input.textChanged.connect(self.update_button_state)

        self.login_button = QPushButton('Войти', self)
        # Устанавливаем начальный стиль кнопки, когда она не активна (белая)
        self.login_button.setStyleSheet(
            "background-color: white; color: #FFA500; padding: 12px; border: 2px solid #FFA500; border-radius: 5px; font-size: 18px;")
        self.login_button.clicked.connect(self.check_credentials)
        self.login_button.setEnabled(False)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def update_button_state(self):
        # Если оба поля заполнены
        if self.username_input.text() and self.password_input.text():
            self.login_button.setEnabled(True)
            # Устанавливаем стиль кнопки как активный (оранжевый)
            self.login_button.setStyleSheet(
                "background-color: #FFA500; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 18px;")
        else:
            self.login_button.setEnabled(False)
            # Устанавливаем стиль кнопки как неактивный (белый фон)
            self.login_button.setStyleSheet(
                "background-color: white; color: #FFA500; padding: 12px; border: 2px solid #FFA500; border-radius: 5px; font-size: 18px;")

    def check_credentials(self):
        login = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not login or not password:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите логин и пароль.', QMessageBox.StandardButton.Ok)
            return
        try:
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Выполняем запрос для проверки логина и пароля
            cursor.execute(
                'SELECT id_librarian, surname, name, otchestvo FROM librarians WHERE login = ? AND password = ?',
                (login, password))
            result = cursor.fetchone()

            if result:
                librarian_id, surname, name, otchestvo = result
                # Если отчество отсутствует, заменяем его на пустую строку
                otchestvo = otchestvo or ""
                librarian_name = f"{surname} {name} {otchestvo}"
                QMessageBox.information(self, 'Успех', 'Вы вошли в систему!', QMessageBox.StandardButton.Ok)
                # Передаем в open_main_window параметры librarian_id и librarian_name
                self.open_main_window(librarian_id, librarian_name)
                self.close()  # Закрываем окно входа
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль.', QMessageBox.StandardButton.Ok)
        except sqlite3.Error as err:
            QMessageBox.critical(self, 'Ошибка базы данных', f'Ошибка: {err}', QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}', QMessageBox.StandardButton.Ok)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def open_main_window(self, librarian_id, librarian_name):
        from main import MainWindow
        self.main_window = MainWindow(librarian_id, librarian_name)
        self.main_window.show()