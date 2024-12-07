from book_details_window import BookDetailsWindow
from reader_records_window import ReaderRecordsWindow
from attendance_report_window import AttendanceReportWindow
from debt_report_window import DebtReportWindow
from login_window import LoginWindow
import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, \
QMainWindow, QHBoxLayout, QListWidget, QListWidgetItem
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QStandardPaths
from datetime import datetime, timedelta
import os


class MainWindow(QMainWindow):
    def __init__(self, librarian_id, librarian_name):
        self.book_details_window = None
        super().__init__()
        self.setWindowTitle('Главное окно')
        self.setGeometry(600, 175, 800, 600)
        # Инициализация атрибутов
        self.librarian_id = librarian_id
        self.librarian_name = librarian_name

        # Вызов функции для вычисления задолженностей при запуске программы
        self.check_debt_on_startup()
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.setup_menu()

    def closeEvent(self, event):
        # Если есть дочернее окно, закрыть его
        if self.book_details_window:
            self.book_details_window.close()
        if self.reader_records_window:
            self.reader_records_window.close()
        if self.report_window:
            self.report_window.close()
        if self.reporti_window:
            self.reporti_window.close()
        event.accept()  # Разрешаем закрытие главного окна

    def check_debt_on_startup(self):
        # Проверка задолженности для всех читателей при запуске программы.
        try:
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Получаем текущую дату
            today = datetime.now().date()

            # Запрос для получения всех не возвращённых книг
            cursor.execute("""
                SELECT r.id_reader, r.id_book, r.date_loan, r.date_return
                FROM records r
                WHERE r.date_return IS NULL""")
            records = cursor.fetchall()
            # Список читателей с просроченными книгами
            readers_with_overdue = set()
            # Проверяем каждую запись
            for record in records:
                reader_id = record[0]
                book_id = record[1]
                issue_date = datetime.strptime(record[2], "%Y-%m-%d").date()

                # Если прошло более 30 дней с даты выдачи
                if today > issue_date + timedelta(days=30):
                    readers_with_overdue.add(reader_id)

                # Проверка на дублирование: чтобы одна и та же книга не пересекалась по датам для одного читателя
                cursor.execute("""
                    SELECT r.id_reader, r.id_book, r.date_loan, r.date_return
                    FROM records r
                    WHERE r.id_reader = ? AND r.id_book = ? AND r.date_return IS NULL""", (reader_id, book_id))
                # Если уже есть активная запись для той же книги (не возвращена)
                overlapping_records = cursor.fetchall()
                if len(overlapping_records) > 1:
                    continue  # Пропускаем дальнейшую обработку для этой книги

            # Если есть читатели с просроченными книгами, обновляем задолженность
            if readers_with_overdue:
                for reader_id in readers_with_overdue:
                    cursor.execute("UPDATE readers SET debt = 1 WHERE id_reader = ?", (reader_id,))
                    conn.commit()

            # Рассчитываем штрафы для просроченных книг
            cursor.execute("""
                SELECT r.id_reader, r.id_book, r.date_loan, b.price, b.status
                FROM records r
                JOIN books b ON r.id_book = b.id_book
                WHERE r.date_return IS NULL""")
            overdue_books = cursor.fetchall()
            for book in overdue_books:
                reader_id = book[0]
                book_id = book[1]
                issue_date = datetime.strptime(book[2], "%Y-%m-%d").date()
                book_price = book[3]
                book_condition = book[4]

                # Если прошло более 30 дней с даты выдачи
                if today > issue_date + timedelta(days=30):
                    # Рассчитываем количество дней просрочки
                    days_late = (today - issue_date).days
                    fine = 0
                    if days_late > 30:
                        fine += (days_late - 30) * (book_price / 10)
                    if book_condition == "плохое":
                        fine += book_price
                    # Убедимся, что штраф не может быть меньше 0
                    fine = max(fine, 0)
                    # Округляем штраф до двух знаков после запятой
                    fine = round(fine, 2)

                    # Обновляем штраф
                    cursor.execute("""
                        UPDATE records 
                        SET fine = ? 
                        WHERE id_reader = ? AND id_book = ? AND date_return IS NULL""", (fine, reader_id, book_id))
                    conn.commit()
        except sqlite3.Error as err:
            QMessageBox.critical(None, 'Ошибка базы данных', f'Ошибка: {err}', QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(None, 'Ошибка', f'Произошла ошибка: {str(e)}', QMessageBox.StandardButton.Ok)
        finally:
            cursor.close()
            conn.close()

    def setup_menu(self):
        # Настройка меню в главном окне.
        menu_bar = self.menuBar()

        system_menu = menu_bar.addMenu(self.librarian_name)
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.logout)
        system_menu.addAction(exit_action)

        file_menu = menu_bar.addMenu('Фонд')
        view_books_action = QAction('Просмотр библиотечного фонда', self)
        view_books_action.triggered.connect(self.show_books_list)
        file_menu.addAction(view_books_action)

        records_menu = menu_bar.addMenu('Учётные карточки')
        records_action = QAction('Просмотр учётных карточек', self)
        records_action.triggered.connect(self.show_reader_records)
        records_menu.addAction(records_action)

        reports_menu = menu_bar.addMenu("Отчёты")
        attendance_action = QAction("Посещаемость", self)
        attendance_action.triggered.connect(self.show_attendance_report)
        reports_menu.addAction(attendance_action)

        debt_action = QAction("Долги", self)
        debt_action.triggered.connect(self.show_debt_report)
        reports_menu.addAction(debt_action)

        # Флаг для проверки наличия поля поиска
        self.search_field_added = False

    def logout(self):
        # Метод для выхода из системы и возвращения на экран авторизации.
        reply = QMessageBox.question(self, 'Выход', 'Вы уверены, что хотите выйти из системы?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Закрываем все открытые окна
            for widget in QApplication.topLevelWidgets():
                if widget.isVisible() and widget != self:
                    widget.close()
            # Закрываем текущее окно
            self.hide()
            # Открываем окно авторизации
            self.login_window = LoginWindow()
            self.login_window.show()

    def closeEvent(self, event):
            QApplication.quit()  # Завершаем приложение
            event.accept()  # Закрытие окна

    def show_books_list(self):
        # Очистка текущего содержимого
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Если поле поиска ещё не добавлено
        if not self.search_field_added:
            search_layout = QHBoxLayout()

            # Поле для ввода поиска
            self.search_input = QLineEdit(self)
            self.search_input.setPlaceholderText("Поиск по названию книги и по ID книги")
            self.search_input.setStyleSheet("""
                padding: 12px;
                font-size: 16px;
                border: 2px solid #FFA500;
                border-radius: 5px;
                background-color: white;""")

            # Кнопка для поиска
            self.search_button = QPushButton("Поиск", self)
            self.search_button.setStyleSheet("""
                background-color: #FFA500;
                border-radius: 5px;
                color: white;
                padding: 12px;
                font-size: 18px;""")
            self.search_button.clicked.connect(self.search_books)

            search_layout.addWidget(self.search_input)
            search_layout.addWidget(self.search_button)
            self.layout.addLayout(search_layout)
            self.search_field_added = True

        # Добавление списка для отображения книг
        self.book_list = QListWidget(self)
        self.book_list.setStyleSheet("""
            font-size: 16px;
            background-color: white;
            color: #333333;""")
        self.layout.addWidget(self.book_list)
        self.load_books()

    def load_books(self, query="SELECT id_book, title, status FROM books ORDER BY title ASC", params=None):
        try:
            # Отключаем обновление интерфейса
            self.setUpdatesEnabled(False)
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Выполняем SQL-запрос
            cursor.execute(query, params if params else ())
            books = cursor.fetchall()
            # Очищаем список книг только если это необходимо
            self.book_list.clear()

            # Добавляем книги в список
            for book in books:
                item = QListWidgetItem(f"{book[1]}")  # Заголовок книги
                item.setData(Qt.ItemDataRole.UserRole, book[0])  # Устанавливаем ID книги
                self.book_list.addItem(item)

            # Подключаем обработчик клика по элементу списка
            self.book_list.itemClicked.connect(self.show_book_details_window)
        except sqlite3.Error as err:
            QMessageBox.critical(self, 'Ошибка базы данных', f'Ошибка: {err}', QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}', QMessageBox.StandardButton.Ok)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            # Включаем обновление интерфейса
            self.setUpdatesEnabled(True)

    def search_books(self):
        search_text = self.search_input.text().strip()
        if search_text:
            # Если введённый текст состоит только из цифр, ищем по ID, иначе ищем по названию
            if search_text.isdigit():
                # Запрос для поиска книги по точному ID
                query = """
                SELECT id_book, title, status
                FROM books
                WHERE id_book = ?
                ORDER BY title ASC"""
                self.load_books(query, (search_text,))  # Ищем только по точному ID
            else:
                # Запрос для поиска книг по названию с сортировкой по алфавиту
                query = """
                SELECT id_book, title, status
                FROM books
                WHERE title LIKE ?
                ORDER BY title ASC"""
                search_term = f"%{search_text}%"  # Ищем по части названия
                self.load_books(query, (search_term,))  # Ищем по части названия
        else:
            # Если текст поиска пуст, загружаем все книги с сортировкой по названию
            self.load_books()  # Без параметров для загрузки всех книг

    def show_book_details_window(self, item):
        book_id = item.data(Qt.ItemDataRole.UserRole)
        # Если окно уже существует, обновим его данные
        if self.book_details_window and self.book_details_window.isVisible():
            self.book_details_window.update_book_details(book_id)
        else:
            # Создаем новое окно с подробностями книги, если оно не открыто
            self.book_details_window = BookDetailsWindow(book_id, self.librarian_id)
            self.book_details_window.show()

    def show_reader_records(self):
        self.reader_records_window = ReaderRecordsWindow()
        self.reader_records_window.show()

    def show_attendance_report(self):
        self.report_window = AttendanceReportWindow()
        self.report_window.show()

    def show_debt_report(self):
        self.reporti_window = DebtReportWindow()
        self.reporti_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())

