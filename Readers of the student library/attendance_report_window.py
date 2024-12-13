import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QComboBox
from PyQt6.QtGui import QPalette, QColor, QPainter, QPixmap
from PyQt6.QtCore import QDate, QStandardPaths
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
import xlsxwriter
import os

class AttendanceReportWindow(QWidget):
    def __init__(self, librarian_id):
        super().__init__()
        self.librarian_id = librarian_id
        self.setWindowTitle("Отчёт по посещаемости")
        self.setFixedSize(400, 340)
        # Макет для виджетов
        self.layout = QVBoxLayout()
        # Виджеты для выбора года и месяца
        self.year_label = QLabel("Год:")
        self.year_label.setStyleSheet("font-size: 15px; color: #333333;")

        self.year_combo = QComboBox()
        self.year_combo.addItems([str(year) for year in range(1990, 3000)])
        self.year_combo.setStyleSheet("""
            padding: 12px 30px 12px 12px;
            font-size: 16px;
            border: 2px solid #FFA500;
            border-radius: 5px;
            background-color: white;""")

        self.year_combo.view().setStyleSheet("""
                    background-color: white;  
                    border: none;  
                    color: #333333;""")

        # Устанавливаем текущий год по умолчанию
        current_year = QDate.currentDate().year()
        self.year_combo.setCurrentText(str(current_year))

        self.month_label = QLabel("Месяц:")
        self.month_label.setStyleSheet("""
            font-size: 15px;
            color: #333333;""")

        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"])
        self.month_combo.setStyleSheet("""
            padding: 12px 30px 12px 12px;
            font-size: 16px;
            border: 2px solid #FFA500;
            border-radius: 5px;
            background-color: white;""")

        self.month_combo.view().setStyleSheet("""
            background-color: white;  
            border: none;  
            color: #333333;""")

        # Устанавливаем текущий месяц по умолчанию
        current_month = QDate.currentDate().month()
        month_name = self.month_combo.itemText(current_month - 1)
        self.month_combo.setCurrentText(month_name)

        # Кнопка для генерации отчёта
        self.generate_button = QPushButton("Сгенерировать отчёт")
        self.generate_button.setStyleSheet("""
            background-color: #FFA500;
            border-radius: 5px;
            color: white;
            padding: 12px;
            font-size: 18px;""")
        self.generate_button.clicked.connect(self.generate_attendance_report)

        # Кнопка для сохранения диаграммы
        self.save_image_button = QPushButton("Сохранить диаграмму")
        self.save_image_button.setStyleSheet("""
            background-color: #FFA500;
            border-radius: 5px;
            color: white;
            padding: 12px;
            font-size: 18px;""")
        self.save_image_button.clicked.connect(self.save_chart_image)

        # Кнопка для экспорта в Excel с диаграммой
        self.export_excel_button = QPushButton("Экспорт в Excel с диаграммой")
        self.export_excel_button.setStyleSheet("""
            background-color: #FFA500;
            border-radius: 5px;
            color: white;
            padding: 12px;
            font-size: 18px;""")
        self.export_excel_button.clicked.connect(self.export_to_excel_with_chart)

        selection_layout = QVBoxLayout()
        selection_layout.addWidget(self.year_label)
        selection_layout.addWidget(self.year_combo)
        selection_layout.addWidget(self.month_label)
        selection_layout.addWidget(self.month_combo)
        selection_layout.addWidget(self.generate_button)
        selection_layout.addWidget(self.save_image_button)
        selection_layout.addWidget(self.export_excel_button)
        self.layout.addLayout(selection_layout)
        # Устанавливаем основной layout для окна
        self.setLayout(self.layout)
        # Диаграмма для отображения посещаемости
        self.chart_view = None

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

    def generate_attendance_report(self, librarian_id):
        self.log_operation("Генерация диаграммы", self.librarian_id)
        self.setMinimumSize(660, 600)
        self.setMaximumSize(1200, 900)
        try:
            year = self.year_combo.currentText()
            month = self.month_combo.currentIndex() + 1  # Индексация месяцев с 1
            # Получаем количество посещений и не посещений
            attendance_count, absent_count = self.get_attendance_count(year, month)

            # Создание круговой диаграммы
            pie_series = QPieSeries()
            # Добавляем сегменты с подсчетом посещений и отсутствующих
            slice_visits = pie_series.append("Читатели, посетившие библиотеку", attendance_count)
            slice_absent = pie_series.append("Читатели, не посетившие библиотеку", absent_count)
            # Настройка цвета для сегментов с использованием QColor
            slice_visits.setColor(QColor(100, 181, 246))  # Голубой для посещений
            slice_absent.setColor(QColor(255, 183, 77))  # Оранжевый для отсутствующих

            # Создание диаграммы
            chart = QChart()
            chart.addSeries(pie_series)
            chart.setTitle(f"Посещаемость за {self.month_combo.currentText()} {year} года")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            # Настройка меток с процентами и количеством
            total_count = attendance_count + absent_count

            # Для первого сегмента (посетившие библиотеку)
            value_visits = slice_visits.value()
            percentage_visits = (value_visits / total_count) * 100
            percentage_visits_rounded = round(percentage_visits)
            slice_visits.setLabel(f"{slice_visits.label()} ({attendance_count} - {percentage_visits_rounded}%)")

            # Для второго сегмента (не посетившие библиотеку)
            value_absent = slice_absent.value()
            percentage_absent = (value_absent / total_count) * 100
            percentage_absent_rounded = round(percentage_absent)
            slice_absent.setLabel(f"{slice_absent.label()} ({absent_count} - {percentage_absent_rounded}%)")

            # Размещение меток снаружи сегмента
            slice_visits.setLabelPosition(QPieSlice.LabelPosition.LabelOutside)
            slice_absent.setLabelPosition(QPieSlice.LabelPosition.LabelOutside)

            # Проверка, существует ли старый виджет диаграммы и удаление его
            if hasattr(self, 'chart_view') and self.chart_view is not None:
                self.chart_view.deleteLater()  # Удаляем старый виджет
            # Создаем представление диаграммы
            self.chart_view = QChartView(chart)
            self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

            layout = QVBoxLayout()
            layout.addWidget(self.chart_view)

            # Добавление нового layout в родительский layout
            self.layout.addLayout(layout)  # Используем новый layout для диаграммы
        except Exception as e:
            print(f"Ошибка при генерации отчёта: {e}")

    def get_attendance_count(self, year, month):
        try:
            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            db_folder_path = os.path.join(desktop_path, "Library")
            db_path = os.path.join(db_folder_path, "library.db")
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            # Выполняем SQL-запрос для получения количества посещений
            cursor.execute("""
                SELECT COUNT(DISTINCT r.id_reader) AS attendance_count
                FROM Records rec
                JOIN Readers r ON rec.id_reader = r.id_reader
                WHERE strftime('%m', rec.date_loan) = ? 
                AND strftime('%Y', rec.date_loan) = ?;
            """, (f"{month:02d}", year))  # Форматируем месяц с ведущим нулем
            attendance_result = cursor.fetchone()
            # Получаем общее количество читателей
            cursor.execute("SELECT COUNT(id_reader) FROM Readers")
            total_readers = cursor.fetchone()[0]
            connection.close()
            attendance_count = attendance_result[0] if attendance_result else 0
            absent_count = total_readers - attendance_count
            return attendance_count, absent_count
        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")
            return 0, 0

    def save_chart_image(self, librarian_id):
        self.log_operation("Сохранение диаграммы в формате .png", self.librarian_id)
        if self.chart_view:
            try:
                # Обновляем виджет диаграммы
                self.chart_view.update()
                # Получаем размеры текущего виджета (диаграммы)
                width = self.chart_view.width()
                height = self.chart_view.height()
                if width <= 0 or height <= 0:
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Ошибка")
                    msg_box.setText("Невозможно захватить изображение. Неправильные размеры виджета.")
                    # Применяем стандартную палитру для кнопок
                    palette = QPalette()
                    msg_box.setPalette(palette)
                    msg_box.setIcon(QMessageBox.Icon.Critical)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.exec()
                    return

                # Получаем текущий год и месяц для имени файла
                year = self.year_combo.currentText()
                month = self.month_combo.currentIndex() + 1  # Индексация месяцев с 1
                # Формируем строку для имени файла
                image_filename = f"Посещаемость_диаграмма_{year}_{month:02d}.png"

                desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
                folder_path = os.path.join(desktop_path, "Отчёты", "Посещаемость")

                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    QMessageBox.information(self, "Информация", f"Папка '{folder_path}' была создана.")
                image_path = os.path.join(folder_path, image_filename)

                if os.path.exists(image_path):
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Информация")
                    msg_box.setText(f"Файл '{image_filename}' уже был сохранён ранее в папку '{folder_path}'.")
                    msg_box.setIcon(QMessageBox.Icon.Information)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.exec()
                    return

                # Создаём QPixmap с белым фоном
                pixmap = QPixmap(width, height)
                pixmap.fill(QColor(255, 255, 255))  # Белый цвет фона
                # Создаём QPainter для рисования
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                # Рисуем на pixmap
                self.chart_view.render(painter)
                painter.end()
                # Сохраняем изображение
                pixmap.save(image_path)

                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Успех")
                msg_box.setText(f"Диаграмма успешно сохранена как '{image_filename}' в папку '{folder_path}'")

                palette = QPalette()
                msg_box.setPalette(palette)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()
            except Exception as e:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Ошибка")
                msg_box.setText(f"Ошибка при сохранении изображения: {e}")
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()

    def export_to_excel_with_chart(self, librarian_id):
        self.log_operation("Сохранение диаграммы в формате .xlsx", self.librarian_id)
        try:
            year = self.year_combo.currentText()
            month = self.month_combo.currentIndex() + 1
            attendance_count, absent_count = self.get_attendance_count(year, month)
            # Создание книги Excel с использованием xlsxwriter
            excel_filename = f"Посещаемость_диаграмма_{year}_{month}.xlsx"

            desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            folder_path = os.path.join(desktop_path, "Отчёты", "Посещаемость")

            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                QMessageBox.information(self, "Информация", f"Папка '{folder_path}' была создана.")
            excel_path = os.path.join(folder_path, excel_filename)

            if os.path.exists(excel_path):
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Информация")
                msg_box.setText(f"Файл '{excel_filename}' уже был экспортирован ранее в папку '{folder_path}'.")
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()
                return

            # Создание книги Excel и добавление данных
            workbook = xlsxwriter.Workbook(excel_path)
            worksheet = workbook.add_worksheet("Отчёт")
            worksheet.set_column('A:A', 33)  # Ширина столбца A (Тип) — 33 символа
            worksheet.set_column('B:B', 10)  # Ширина столбца B (Количество) — 10 символов

            # Добавляем данные для диаграммы
            worksheet.write("A1", "Тип")
            worksheet.write("B1", "Количество")
            worksheet.write("A2", "Читатели, посетившие библиотеку")
            worksheet.write("B2", attendance_count)
            worksheet.write("A3", "Читатели, не посетившие библиотеку")
            worksheet.write("B3", absent_count)
            # Создаём круговую диаграмму
            chart = workbook.add_chart({'type': 'pie'})

            # Добавляем серию данных для диаграммы
            chart.add_series({
                'name': f"Посещаемость за {self.month_combo.currentText()} {year} года",
                'categories': '=Отчёт!$A$2:$A$3',  # Диапазон категорий (Типы)
                'values': '=Отчёт!$B$2:$B$3',  # Диапазон значений (Количество)
                'data_labels': {
                    'value': True,  # Отображаем значения
                    'percentage': True,  # Отображаем проценты
                    'number_format': '0.00%',  # Форматируем как проценты
                    'position': 'outside_end',  # Размещение меток снаружи
                },
                'points': [
                    {'fill': {'color': '#64B5F6'}},
                    {'fill': {'color': '#FFB74D'}},],})

            # Вставляем диаграмму в Excel
            worksheet.insert_chart('A5', chart)
            # Закрытие и сохранение файла
            workbook.close()
            QMessageBox.information(self, "Успех",
                                    f"Отчёт с диаграммой успешно экспортирован в Excel как '{excel_filename}' в папку '{folder_path}'")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте в Excel: {e}")