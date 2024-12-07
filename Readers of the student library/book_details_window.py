import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox, QDateEdit
from PyQt6.QtCore import QDate, QStandardPaths
from datetime import datetime
import os

class BookDetailsWindow(QWidget):  # Окно с подробной информацией о книге
    def __init__(self, book_id, librarian_id):
        super().__init__()
        self.setWindowTitle('Подробности о книге')
        self.setFixedSize(400, 300)
        self.librarian_id = librarian_id
        self.book_id = book_id
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-size: 15px;
                font-family: Arial, sans-serif;
                color: #333333;
            }""")

        title_label = QLabel(
            '<h2 style="color: #FFA500; text-align: center;">Подробности о книге</h2>')
        self.layout.addWidget(title_label)

        # Кнопка выдачи книги
        self.issue_button = QPushButton('Выдача книги', self)
        self.issue_button.setStyleSheet("background-color: #FFA500; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 18px;")
        self.issue_button.clicked.connect(self.show_issue_fields)
        self.layout.addWidget(self.issue_button)

        # Кнопка возврата книги
        self.return_button = QPushButton('Возврат книги', self)
        self.return_button.setStyleSheet("background-color: #FFA500; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 18px;")
        self.return_button.clicked.connect(self.show_return_fields)
        self.layout.addWidget(self.return_button)

        # Поля для ввода данных (спрятаны изначально)
        self.surname_input = QLineEdit(self)
        self.surname_label = QLabel("Фамилия:", self)
        self.surname_input.setStyleSheet("padding: 12px; font-size: 16px; border: 2px solid #FFA500; border-radius: 5px;")
        self.surname_input.setVisible(False)
        self.surname_label.setVisible(False)

        self.name_input = QLineEdit(self)
        self.name_label = QLabel("Имя:", self)
        self.name_input.setStyleSheet("padding: 12px; font-size: 16px; border: 2px solid #FFA500; border-radius: 5px;")
        self.name_input.setVisible(False)
        self.name_label.setVisible(False)

        self.otchestvo_input = QLineEdit(self)
        self.otchestvo_label = QLabel("Отчество:", self)
        self.otchestvo_input.setStyleSheet("padding: 12px; font-size: 16px; border: 2px solid #FFA500; border-radius: 5px;")
        self.otchestvo_input.setVisible(False)
        self.otchestvo_label.setVisible(False)

        self.reader_id_input = QLineEdit(self)
        self.reader_id_label = QLabel("ID читателя:", self)
        self.reader_id_input.setStyleSheet("padding: 12px; font-size: 16px; border: 2px solid #FFA500; border-radius: 5px;")
        self.reader_id_input.setVisible(False)
        self.reader_id_label.setVisible(False)

        self.issue_date_label = QLabel("Дата выдачи:", self)
        self.layout.addWidget(self.issue_date_label)
        self.issue_date_label.setVisible(False)

        # Поле для ввода даты возврата
        self.issue_date_input = QDateEdit(self)
        self.issue_date_input.setDisplayFormat("yyyy-MM-dd")  # Формат отображения
        self.issue_date_input.setDate(QDate.currentDate())  # Устанавливаем текущую дату
        self.issue_date_input.setCalendarPopup(True)  # Включаем всплывающее окно календаря
        self.issue_date_input.setStyleSheet("""
                    QDateEdit {
                        padding: 12px;
                        font-size: 16px;
                        border: 2px solid #FFA500;
                        border-radius: 5px;
                    }
                    QCalendarWidget {
                        border: none;  
                    }""")
        self.issue_date_input.setVisible(False)
        self.layout.addWidget(self.issue_date_input)

        self.issue_button_confirm = QPushButton('Подтвердить выдачу', self)
        self.issue_button_confirm.setStyleSheet("background-color: #FFA500; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 18px;")
        self.issue_button_confirm.clicked.connect(self.issue_book)
        self.issue_button_confirm.setVisible(False)

        self.layout.addWidget(self.surname_label)
        self.layout.addWidget(self.surname_input)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.otchestvo_label)
        self.layout.addWidget(self.otchestvo_input)
        self.layout.addWidget(self.reader_id_label)
        self.layout.addWidget(self.reader_id_input)
        self.layout.addWidget(self.issue_date_label)
        self.layout.addWidget(self.issue_date_input)
        self.layout.addWidget(self.issue_button_confirm)

        self.reader_if_label = QLabel("ID читателя:", self)
        self.layout.addWidget(self.reader_if_label)
        self.reader_if_label.setVisible(False)
        self.reader_if_input = QLineEdit(self)
        self.reader_if_input.setStyleSheet("padding: 12px; font-size: 16px; border: 2px solid #FFA500; border-radius: 5px;")
        self.reader_if_input.setVisible(False)
        self.layout.addWidget(self.reader_if_input)

        self.date_label = QLabel("Дата возврата:", self)
        self.layout.addWidget(self.date_label)
        self.date_label.setVisible(False)
        self.return_date_input = QDateEdit(self)
        self.return_date_input.setDisplayFormat("yyyy-MM-dd")  # Формат отображения
        self.return_date_input.setDate(QDate.currentDate())  # Устанавливаем текущую дату
        self.return_date_input.setCalendarPopup(True)  # Включаем всплывающее окно календаря
        self.return_date_input.setStyleSheet("""
            QDateEdit {
                padding: 12px;
                font-size: 16px;
                border: 2px solid #FFA500;
                border-radius: 5px;}
            QCalendarWidget {
                border: none;}""")
        self.return_date_input.setVisible(False)
        self.layout.addWidget(self.return_date_input)

        self.condition_label = QLabel("Состояние книги:", self)
        self.layout.addWidget(self.condition_label)
        self.condition_label.setVisible(False)
        self.book_condition_input = QComboBox(self)
        self.book_condition_input.addItem("хорошее")
        self.book_condition_input.addItem("плохое")
        self.book_condition_input.setStyleSheet("""
            /* Стиль для поля ввода */
            QComboBox {
                padding: 12px 30px 12px 12px;
                font-size: 16px;
                border: 2px solid #FFA500; 
                border-radius: 5px;}
            /* Стиль для выпадающего списка */
            QComboBox QAbstractItemView {
                background-color: white; 
                border: none;  
                color: #333333;  }""")
        self.book_condition_input.setVisible(False)
        self.layout.addWidget(self.book_condition_input)

        # Кнопка для подтверждения возврата
        self.return_button_confirm = QPushButton('Подтвердить возврат', self)
        self.return_button_confirm.setStyleSheet("background-color: #FFA500; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 18px;")
        self.return_button_confirm.clicked.connect(self.return_book)
        self.return_button_confirm.setVisible(False)
        self.layout.addWidget(self.return_button_confirm)

        # Инициализация контейнера для меток с данными о книге
        self.book_labels = {}
        # Загружаем информацию о книге
        self.load_book_details()

    def load_book_details(self):
        self.setUpdatesEnabled(False)
        try:
            # Получаем путь к рабочему столу
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            # Формируем путь к папке на рабочем столе
            db_folder_path = os.path.join(desktop_path, "Library")
            # Формируем путь к базе данных
            db_path = os.path.join(db_folder_path, "library.db")
            # Подключение к базе данных SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            query = "SELECT title, surname, name, otchestvo, date_publication, status, price FROM books WHERE id_book = ?"
            cursor.execute(query, (self.book_id,))
            book = cursor.fetchone()

            if book:
                self.price_one = float(book[6])
                # Удаляем старые метки, если они есть
                for label in self.book_labels.values():
                    label.deleteLater()

                # Добавляем новые метки
                self.book_labels['title'] = QLabel(f"Название: {book[0]}")
                self.layout.addWidget(self.book_labels['title'])

                self.book_labels['author'] = QLabel(f"Автор: {book[1]} {book[2]} {book[3]}")
                self.layout.addWidget(self.book_labels['author'])

                publication_date = datetime.strptime(book[4], '%Y-%m-%d').strftime('%Y-%m-%d')
                self.book_labels['publication_date'] = QLabel(f"Год выпуска: {publication_date}")
                self.layout.addWidget(self.book_labels['publication_date'])

                self.book_labels['status'] = QLabel(f"Состояние: {book[5]}")
                self.layout.addWidget(self.book_labels['status'])

                self.book_labels['price'] = QLabel(f"Стоимость: {self.price_one:.2f} RUB")
                self.layout.addWidget(self.book_labels['price'])

                if book[5] == "выдана":  # Если книга выдана, активируем кнопку возврата
                    self.return_button.setEnabled(True)
                    self.issue_button.setEnabled(False)
                else:
                    self.return_button.setEnabled(False)
            else:
                self.layout.addWidget(QLabel("Информация о книге не найдена"))
        except sqlite3.Error as err:
            QMessageBox.critical(self, 'Ошибка базы данных', f'Ошибка: {err}', QMessageBox.StandardButton.Ok)
        finally:
            cursor.close()
            conn.close()
        self.setUpdatesEnabled(True)

    def update_book_details(self, book_id):
        # Метод для обновления информации в окне с деталями книги.
        self.book_id = book_id  # Обновляем ID книги
        self.load_book_details()  # Перезагружаем детали книги

    def show_issue_fields(self):
        self.setMinimumSize(400, 600)
        self.setMaximumSize(500, 700)
        self.issue_button.setVisible(False)
        self.return_button.setVisible(False)

        self.surname_label.setVisible(True)
        self.surname_input.setVisible(True)
        self.name_label.setVisible(True)
        self.name_input.setVisible(True)
        self.otchestvo_label.setVisible(True)
        self.otchestvo_input.setVisible(True)
        self.reader_id_label.setVisible(True)
        self.reader_id_input.setVisible(True)
        self.issue_date_label.setVisible(True)
        self.issue_date_input.setVisible(True)
        self.issue_button_confirm.setVisible(True)

    def show_return_fields(self):
        self.setMinimumSize(400, 440)
        self.setMaximumSize(500, 500)
        self.return_button.setVisible(False)
        self.issue_button.setVisible(False)

        self.date_label.setVisible(True)
        self.return_date_input.setVisible(True)
        self.reader_if_label.setVisible(True)
        self.reader_if_input.setVisible(True)
        self.condition_label.setVisible(True)
        self.book_condition_input.setVisible(True)
        self.return_button_confirm.setVisible(True)

    def return_book(self):
        # Получаем введённые данные
        reader_if = self.reader_if_input.text().strip()
        return_date = self.return_date_input.text().strip()
        book_condition = self.book_condition_input.currentText().strip().lower()

        # Проверка на пустые поля
        if not reader_if or not return_date or not book_condition:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения!")
            return
        try:
            return_date_obj = datetime.strptime(return_date, "%Y-%m-%d").date()  # Преобразуем строку в дату
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Получаем данные о выдаче книги для указанного ID читателя
            cursor.execute("""
                SELECT date_loan, id_reader, price 
                FROM records
                INNER JOIN books ON records.id_book = books.id_book
                WHERE records.id_book = ? AND date_return IS NULL
            """, (self.book_id,))
            record = cursor.fetchone()

            if not record:
                QMessageBox.warning(self, "Ошибка", "Не найдена запись о выдаче книги.")
                return

            issue_date = datetime.strptime(record[0], "%Y-%m-%d").date()
            reader_id = record[1]
            book_price = record[2]

            # Проверяем, что ID читателя совпадает с введенным
            if reader_if != str(reader_id):
                QMessageBox.warning(self, "Ошибка", "Эта книга не была выдана указанному читателю!")
                return

            # Проверяем, что дата возврата не раньше даты выдачи
            if return_date_obj < issue_date:
                QMessageBox.warning(self, "Ошибка", "Дата возврата не может быть раньше даты выдачи.")
                return

            # Рассчитываем просрочку
            days_late = (return_date_obj - issue_date).days
            fine = 0

            # Штраф за каждый день просрочки начисляется только после 30 дней
            if days_late > 30:
                fine = (days_late - 30) * (book_price / 10)  # 1/10 стоимости книги за каждый день просрочки

            # Если книга в плохом состоянии, штраф равен полной стоимости книги
            if book_condition == "плохое":
                fine += book_price  # Полная стоимость книги как штраф за плохое состояние

            # Гарантируем, что штраф не будет меньше 0
            fine = max(fine, 0)

            # Округляем штраф до двух знаков после запятой
            fine = round(fine, 2)

            if fine > 0:
                # Выводим информацию о штрафе с округленным значением
                QMessageBox.information(self, "Штраф", f"Штраф составляет: {fine:.2f} рублей.")

            # Обновляем статус книги в зависимости от состояния
            if book_condition == "хорошее":
                cursor.execute("UPDATE books SET status = 'хорошее' WHERE id_book = ?", (self.book_id,))
            else:
                cursor.execute("UPDATE books SET status = 'плохое' WHERE id_book = ?", (self.book_id,))

            # Обновляем запись о возврате в таблице records для конкретной записи
            cursor.execute("""
                UPDATE records 
                SET date_return = ?, fine = ? 
                WHERE id_book = ? AND id_reader = ? AND date_return IS NULL
            """, (return_date, fine, self.book_id, reader_id))

            if days_late > 30:
                cursor.execute("UPDATE readers SET debt = 0 WHERE id_reader = ?",(reader_id,))
            conn.commit()
            QMessageBox.information(self, "Успех", "Книга успешно возвращена!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def issue_book(self):
        # Получаем введённые данные
        surname = self.surname_input.text().strip()
        name = self.name_input.text().strip()
        otchestvo = self.otchestvo_input.text().strip()
        reader_id = self.reader_id_input.text().strip()
        issue_date = self.issue_date_input.text().strip()

        if not (surname and name and otchestvo and reader_id and issue_date):
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены.")
            return

        # Проверка, есть ли задолженность
        try:
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Проверка совпадения данных читателя
            cursor.execute("SELECT surname, name, otchestvo FROM readers WHERE id_reader = ?", (reader_id,))
            reader_data = cursor.fetchone()
            if reader_data != (surname, name, otchestvo):
                QMessageBox.warning(self, "Ошибка", "Данные читателя не совпадают с базой данных.")
                return

            # Проверяем, есть ли у читателя просроченные книги
            cursor.execute("""
                SELECT r.id_book
                FROM records r
                JOIN books b ON r.id_book = b.id_book
                WHERE r.id_reader = ? AND r.date_return IS NULL AND julianday(?) - julianday(r.date_loan) > 30
            """, (reader_id, issue_date))
            overdue_books = cursor.fetchall()

            if overdue_books:
                # Если есть хотя бы одна просроченная книга
                cursor.execute("UPDATE readers SET debt = 1 WHERE id_reader = ?", (reader_id,))
                conn.commit()  # Обновляем задолженность в базе

                # Затем проверяем задолженность
                cursor.execute("SELECT debt FROM readers WHERE id_reader = ?", (reader_id,))
                debt = cursor.fetchone()

                if debt and debt[0] == 1:
                    QMessageBox.warning(self, "Ошибка",
                                        "У этого читателя есть просроченные книги. Он не может взять новую книгу.")
                    self.close()
                    return

            # Проверяем наличие неоплаченных штрафов для уже возвращенных книг
            cursor.execute("""
                        SELECT r.id_book, r.fine
                        FROM Records r
                        WHERE r.id_reader = ? AND r.date_return IS NOT NULL AND r.fine > 0 
                    """, (reader_id,))
            unpaid_fines = cursor.fetchall()

            if unpaid_fines:
                # Если есть неоплаченные штрафы
                QMessageBox.warning(self, "Ошибка", "У этого читателя есть неоплаченные штрафы за возвращённые книги. Он не может взять новую книгу.")
                self.close()
                return

            # Проверка статуса книги
            cursor.execute("SELECT status FROM books WHERE id_book = ?", (self.book_id,))
            book_status = cursor.fetchone()[0]
            if book_status == "выдана":
                QMessageBox.warning(self, "Ошибка", "Эта книга уже выдана.")
                return
            # Обновляем статус книги и добавляем запись о выдаче
            cursor.execute("UPDATE books SET status = 'выдана' WHERE id_book = ?", (self.book_id,))

            # Вставляем запись в таблицу Records
            cursor.execute("""
                INSERT INTO records (id_reader, id_book, id_librarian, date_loan)
                VALUES (?, ?, ?, ?)
            """, (reader_id, self.book_id, self.librarian_id, issue_date))
            conn.commit()
            QMessageBox.information(self, "Успех", "Книга успешно выдана!")
            self.close()
        except sqlite3.Error as err:
            QMessageBox.critical(self, 'Ошибка базы данных', f'Ошибка: {err}', QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Произошла ошибка: {str(e)}', QMessageBox.StandardButton.Ok)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()