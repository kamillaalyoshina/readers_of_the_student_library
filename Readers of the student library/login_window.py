import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QStandardPaths
import os


class LoginWindow(QWidget):  # Окно для авторизации
    def __init__(self):
        super().__init__()
        self.create_database()
        self.initUI()

    @staticmethod
    def create_database():
        try:
            # Получение пути к рабочему столу
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")

            # Флаг для проверки, нужно ли показывать сообщение
            show_message = False

            # Создание папки, если она не существует
            if not os.path.exists(db_folder_path):
                os.makedirs(db_folder_path)
                show_message = True

            # Проверка существования файла базы данных
            if not os.path.exists(db_path):
                show_message = True

            # Подключение к базе данных
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Создание таблицы "Библиотекари"
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Librarians (
                    id_librarian INTEGER PRIMARY KEY AUTOINCREMENT,
                    surname TEXT NOT NULL,
                    name TEXT NOT NULL,
                    otchestvo TEXT,
                    number TEXT(11),
                    login TEXT(20) NOT NULL,
                    password TEXT(20) NOT NULL
                )
            """)

            # Создание таблицы "Читатели"
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Readers (
                    id_reader INTEGER PRIMARY KEY AUTOINCREMENT,
                    surname TEXT NOT NULL,
                    name TEXT NOT NULL,
                    otchestvo TEXT,
                    number TEXT(11),
                    debt BOOLEAN NOT NULL DEFAULT 0
                )
            """)

            # Создание таблицы "Книги"
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Books (
                    id_book INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    name TEXT NOT NULL,
                    otchestvo TEXT,
                    date_publication DATE,
                    price REAL NOT NULL,
                    status TEXT CHECK(status IN ('хорошее', 'плохое', 'выдана')) NOT NULL
                )
            """)

            # Создание таблицы "Учётные карточки"
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Records (
                    id_record INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_reader INTEGER,
                    id_book INTEGER,
                    id_librarian INTEGER,
                    date_loan DATE NOT NULL,
                    date_return DATE,
                    fine REAL DEFAULT 0,
                    FOREIGN KEY (id_reader) REFERENCES Readers(id_reader),
                    FOREIGN KEY (id_book) REFERENCES Books(id_book),
                    FOREIGN KEY (id_librarian) REFERENCES Librarians(id_librarian)
                )
            """)

            # Создание таблицы "Log"
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Log (
                    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    id_librarian INTEGER,
                    FOREIGN KEY (id_librarian) REFERENCES Librarians(id_librarian)
                )
            """)

            # Сохранение изменений
            conn.commit()

            # Показ сообщения только если база данных была создана
            if show_message:
                QMessageBox.information(
                    None,
                    "База данных создана",
                    f"База данных успешно создана в папке:\n{db_folder_path}\n"
                    "Необходимо заполнить базу данных перед началом работы.",
                    QMessageBox.StandardButton.Ok
                )

        except sqlite3.Error as e:
            print(f"Ошибка создания базы данных: {e}")

        finally:
            # Закрытие соединения
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def log_operation(operation, id_librarian):
        desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        db_folder_path = os.path.join(desktop_path, "Library")
        db_path = os.path.join(db_folder_path, "library.db")

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO Log (operation, id_librarian) VALUES (?, ?)",
                (operation, id_librarian)
            )

            conn.commit()

        except sqlite3.Error as e:
            print(f"Ошибка записи логов: {e}")

        finally:
            if 'conn' in locals():
                conn.close()

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
                self.log_operation("Авторизация", librarian_id)
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