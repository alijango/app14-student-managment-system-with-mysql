import pymysql as pymysql
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, \
    QPushButton, QLineEdit, QMessageBox, QMainWindow, QMenuBar, QTableWidget, \
    QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, \
    QGridLayout
import sys
from datetime import datetime
import traceback
import sqlite3
import mysql.connector


# Custom exception handler to handle uncaught exceptions.
def handle_exception(exc_type, exc_value, exc_traceback):
    # If the exception is a KeyboardInterrupt (e.g., Ctrl+C), pass it to the default handler.
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # Print the type and value of the uncaught exception.
    print("Uncaught exception:", exc_type, exc_value)
    # Print the traceback of where the exception occurred.
    traceback.print_tb(exc_traceback)


class DataBaseConnection:
    def __init__(self, host='localhost', user='root',
                 password='@Anzelina9912', database='school'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = pymysql.connect(host=self.host, user=self.user,

                                     password=self.password,
                                     database=self.database)

        print("Connection successful")

        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Management System')
        self.setMinimumSize(800, 600)

        # Add menus to the menu bar
        file_menu_item = self.menuBar().addMenu('&File')
        help_menu_item = self.menuBar().addMenu('&Help')
        edit_menu_item = self.menuBar().addMenu('&Edit')

        # Add actions to the File menu
        add_student_action = QAction(QIcon('icons/icons/add.png'),
                                     "Add Record", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction('About', self)
        help_menu_item.addAction(about_action)

        search_action = QAction(QIcon('icons/icons/search.png'),
                                'Search Student', self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('id', 'Name', 'Course', 'Mobile'))
        self.table.verticalHeader()
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        tool_bar = QToolBar()
        tool_bar.setMovable(True)
        self.addToolBar(tool_bar)

        tool_bar.addAction(add_student_action)
        tool_bar.addAction(search_action)

        # Creat a status bar and add status bar elements.

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton('Edit Record')
        edit_button.clicked.connect(self.edite)

        delete_button = QPushButton('Delete Record')
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM students')
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(data)))
        connection.close()

    @staticmethod
    def insert():
        dialog = InsertDialog()
        dialog.exec()

    @staticmethod
    def search():
        search = SearchDialog()
        search.exec()

    @staticmethod
    def edite():
        edite = EditDialog()
        edite.exec()

    @staticmethod
    def delete():
        delete = DeleteDialog()
        delete.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Insert Student data')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText('Mobile')
        layout.addWidget(self.mobile)

        button = QPushButton('Register')
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.currentText()
        mobile = self.mobile.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO students (name, course, mobile) VALUES (%s,%s,%s)',
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle('Search Student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Search')
        layout.addWidget(self.student_name)

        # Create Button
        button = QPushButton('Search')
        button.clicked.connect(self.search_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def search_student(self):
        name = self.student_name.text().strip()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM students WHERE name=%s', (name,))
        cursor.fetchall()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item.row())
            main_window.table.item(item.row(), 1).setSelected(True)
        cursor.close()
        connection.close()

    def search_student_2(self):
        name = self.student_name.text().strip()  # Ensure no leading/trailing spaces
        connection = DataBaseConnection().connect()

        try:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM students WHERE name = %s',
                           (name,))  # Tuple with a trailing comma
            result = cursor.fetchall()

            if result:
                print("Search Results:", result)
            else:
                print("No matching student found.")

        except sqlite3.Error as e:
            print("An error occurred:", e)

        finally:
            connection.close()  # Always close the connection

        #self.table.selectRow(result)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Update Student data')
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        # Get student name from selected row
        #index = main_window.table.currentIndex()
        #row = index.row() or
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        # Get student id from row
        self.student_id = main_window.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # Add combo box for courses
        course = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText('Mobile')
        layout.addWidget(self.mobile)

        button = QPushButton('Update')
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s',
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Delete Student Data')
        student = EditDialog()
        student_name = student.student_name.text()

        layout = QGridLayout()

        confirmation = QLabel(f'Are you sure you want to delete student {student_name} ?')
        yes = QPushButton('Yes')
        no = QPushButton('No')

        # Add widgets
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

        no.clicked.connect(self.cancel_delete)

    def delete_student(self):
        # I think row name netter then index bec item take row arg
        # name = ?, course = ?, mobile = ? WHERE id = ?
        row = main_window.table.currentRow()
        student_id = main_window.table.item(row, 0).text()

        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))

        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Record was deleted successfully!")
        confirmation_widget.exec()

    def cancel_delete(self):
        self.close()
        main_window.load_data()


sys.excepthook = handle_exception

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        main_window.load_data()
        sys.exit(app.exec())
    except Exception as e:
        print(f'an error accured {e}')
