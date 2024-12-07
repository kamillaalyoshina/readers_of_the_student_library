import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt6.QtCore import Qt, QStandardPaths
import os

class ReaderRecordsWindow(QWidget):  # Окно для учётных карточек
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Учётные карточки')
        self.setGeometry(10, 175, 1500, 600)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: Arial, sans-serif;}""")

        # Флаг для проверки наличия поля поиска
        self.search_field_added = False
        if not self.search_field_added:
            search_layout = QHBoxLayout()
            self.search_input = QLineEdit(self)
            self.search_input.setPlaceholderText("Введите ID читателя")
            self.search_input.setStyleSheet("""
                QLineEdit {
                    padding: 12px;
                    font-size: 16px;
                    border: 2px solid #FFA500;
                    border-radius: 5px;
                    width: 300px;}""")

            self.search_button = QPushButton("Поиск", self)
            self.search_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFA500;
                    border-radius: 5px;
                    color: white;
                    padding: 12px;
                    font-size: 18px;
                    width: 120px;}
                QPushButton:disabled {
                    background-color: #D3D3D3;}""")

            self.search_button.clicked.connect(self.search_reader_records)  # Обработчик для поиска
            search_layout.addWidget(self.search_input)
            search_layout.addWidget(self.search_button)
            self.layout.addLayout(search_layout)
            self.search_field_added = True

        # Добавление таблицы для отображения учётных карточек
        self.table = QTableWidget(self)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #CCCCCC;
                background-color: white;
                font-size: 16px;}
            QTableWidget::item {
                padding: 10px;}
            QHeaderView::section {
                font-size: 15px; 
                padding: 10px; 
                text-align: center; }""")
        self.layout.addWidget(self.table)
        self.load_reader_records()  # Загружаем все записи по умолчанию

    def load_reader_records(self, reader_id=None):
        # Загружает учётные карточки в таблицу. Если передан reader_id, фильтрует по нему.
        try:
            # Получаем путь к рабочему столу
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Запрос для получения данных о читателе, книге, дате выдачи и возврата, штрафе, а также библиотекаре
            base_query = """SELECT readers.surname AS reader_surname, readers.name AS reader_name, readers.otchestvo AS reader_otchestvo,
                                       books.title AS book_title, records.date_loan, records.date_return, records.fine,
                                       librarians.surname AS librarian_surname, librarians.name AS librarian_name
                                FROM records
                                JOIN readers ON records.id_reader = readers.id_reader
                                JOIN books ON records.id_book = books.id_book
                                JOIN librarians ON records.id_librarian = librarians.id_librarian"""
            if reader_id:
                base_query += " WHERE records.id_reader = ?"
            # Добавляем сортировку по дате выдачи
            base_query += " ORDER BY records.date_loan DESC"
            cursor.execute(base_query, (reader_id,) if reader_id else ())
            records = cursor.fetchall()

            # Настройка таблицы
            self.table.setRowCount(len(records))
            self.table.setColumnCount(9)  # 9 столбцов
            self.table.setHorizontalHeaderLabels(
                ['Фамилия читателя', 'Имя читателя', 'Отчество читателя', 'Название книги', 'Дата выдачи',
                 'Дата возврата', 'Штраф', 'Фамилия библиотекаря', 'Имя библиотекаря'])

            # Устанавливаем фиксированную ширину для каждого столбца
            column_widths = [150, 150, 150, 250, 120, 190, 100, 200, 150]
            for col, width in enumerate(column_widths):
                self.table.setColumnWidth(col, width)

            # Устанавливаем фиксированную высоту для каждой строки
            row_height = 35
            row_count = self.table.rowCount()
            for row in range(row_count):
                self.table.setRowHeight(row, row_height)

            # Заполнение таблицы данными
            for row, record in enumerate(records):
                for col, value in enumerate(record):
                    if col == 6:
                        value = f"{value:.2f} RUB" if value is not None else "0.00"  # Форматируем штраф
                    item = QTableWidgetItem(str(value))  # Создаём элемент для таблицы
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Блокируем редактирование
                    self.table.setItem(row, col, item)  # Добавляем элемент в таблицу
        except sqlite3.Error as err:
            QMessageBox.critical(self, 'Ошибка базы данных', f'Ошибка: {err}', QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}', QMessageBox.StandardButton.Ok)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def search_reader_records(self):
        # Обработчик кнопки поиска для фильтрации по ID читателя.
        reader_id = self.search_input.text().strip()
        if reader_id:
            if reader_id.isdigit():  # Проверяем, что введён ID числовой
                self.load_reader_records(reader_id=int(reader_id))  # Загружаем записи для конкретного читателя
            else:
                QMessageBox.warning(self, 'Неверный ввод', 'Пожалуйста, введите корректный ID читателя.',
                                    QMessageBox.StandardButton.Ok)
        else:
            self.load_reader_records()  # Если поле пустое, загружаем все записи