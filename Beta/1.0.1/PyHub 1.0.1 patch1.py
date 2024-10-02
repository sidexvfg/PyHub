import sys
import json
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog,
                             QVBoxLayout, QWidget, QPushButton, QTextEdit,
                             QAction, QStatusBar, QTabWidget, QDialog,
                             QLineEdit, QListWidget, QDockWidget, 
                             QInputDialog, QLabel)
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QProcess, QTimer


class FileBrowser(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Browser")
        self.setGeometry(300, 100, 200, 400)

        self.file_list_widget = QListWidget()
        self.file_list_widget.itemDoubleClicked.connect(self.open_selected_file)

        layout = QVBoxLayout()
        layout.addWidget(self.file_list_widget)
        self.setWidget(self.file_list_widget)

        self.load_files()

    def load_files(self):
        import os
        for file in os.listdir('.'):
            if file.endswith('.py'):
                self.file_list_widget.addItem(file)

    def open_selected_file(self, item):
        file_path = item.text()
        editor.open_file(file_path)


class SnippetManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Code Snippets")
        self.setGeometry(100, 100, 300, 400)

        self.snippets_list = QListWidget(self)
        self.load_snippets()

        add_button = QPushButton("Add Snippet", self)
        add_button.clicked.connect(self.add_snippet)

        edit_button = QPushButton("Edit Snippet", self)
        edit_button.clicked.connect(self.edit_snippet)

        delete_button = QPushButton("Delete Snippet", self)
        delete_button.clicked.connect(self.delete_snippet)

        layout = QVBoxLayout()
        layout.addWidget(self.snippets_list)
        layout.addWidget(add_button)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        self.setLayout(layout)

    def load_snippets(self):
        self.snippets_list.addItems([
            "print('Hello, World!')", 
            "for i in range(10):", 
            "if __name__ == '__main__':"
        ])

    def add_snippet(self):
        new_snippet, ok = QInputDialog.getText(self, "Add Snippet", "Snippet:")
        if ok and new_snippet:
            self.snippets_list.addItem(new_snippet)

    def edit_snippet(self):
        item = self.snippets_list.currentItem()
        if item:
            new_snippet, ok = QInputDialog.getText(self, "Edit Snippet", "Edit your snippet:", text=item.text())
            if ok and new_snippet:
                item.setText(new_snippet)

    def delete_snippet(self):
        item = self.snippets_list.currentItem()
        if item:
            self.snippets_list.takeItem(self.snippets_list.row(item))


class ResourceManager(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resource Manager")
        self.setGeometry(400, 100, 250, 400)

        self.resource_list = QListWidget(self)
        self.load_resources()

        self.setWidget(self.resource_list)

    def load_resources(self):
        self.resource_list.addItems(["image1.png", "style.css", "script.js"])  # 示例资源


class TaskManager(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Manager")
        self.setGeometry(600, 100, 300, 400)

        self.task_list = QListWidget()
        self.add_task_button = QPushButton("Add Task", self)
        self.add_task_button.clicked.connect(self.add_task)

        layout = QVBoxLayout()
        layout.addWidget(self.task_list)
        layout.addWidget(self.add_task_button)

        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)

    def add_task(self):
        task_text, ok = QInputDialog.getText(self, "New Task", "Task description:")
        if ok and task_text:
            self.task_list.addItem(task_text)


class ProjectManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project Manager")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()
        label = QLabel("Project Manager is under construction.")
        layout.addWidget(label)
        self.setLayout(layout)


class PythonEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Editor")
        self.setGeometry(100, 100, 800, 600)

        self.apply_styles()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.add_new_tab()

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: white;")

        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("Enter command here...")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_code)  # 连接到 run_code 方法
        layout.addWidget(run_button)

        # 添加 Stop 按钮
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_code)
        self.stop_button.setVisible(False)  # 初始隐藏
        layout.addWidget(self.stop_button)

        # 输出控制台
        layout.addWidget(self.console_output)

        # 控制台输入
        layout.addWidget(self.console_input)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.file_browser = FileBrowser(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_browser)

        self.resource_manager = ResourceManager(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.resource_manager)

        self.task_manager = TaskManager(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.task_manager)

        self.create_menu()
        self.load_user_preferences()

        # 使用QTimer进行自动保存
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # 每30秒运行一次

        self.console_input.returnPressed.connect(self.execute_command)

        # QProcess for running scripts
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def run_code(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            code = current_tab.text()
            with open('temp_script.py', 'w', encoding='utf-8') as script_file:
                script_file.write(code)

            self.stop_button.setVisible(True)
            self.statusBar().showMessage("Code is running...")

            # Start QProcess to run the code
            self.process.start('python', ['temp_script.py'])

    def stop_code(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()  # 终止运行中的进程
            self.console_output.append("Code execution stopped.")
            self.stop_button.setVisible(False)  # 隐藏 Stop 按钮
            self.statusBar().showMessage("Code execution stopped.")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.console_output.append(str(data, encoding='utf-8'))

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.console_output.append(str(data, encoding='utf-8'))

    def process_finished(self):
        self.stop_button.setVisible(False)  # 隐藏 Stop 按钮
        self.statusBar().showMessage("Code execution finished.")

    def auto_save(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            file_name = current_tab.windowTitle()
            # 检查文件名是否有效
            if file_name and file_name != "新建文件":  # 确保文件名不为空且不是新建文件
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(current_tab.text())
                self.statusBar().showMessage(f"Autosaved: {file_name}")

    def add_new_tab(self, text='', title='新建文件'):
        tab = QsciScintilla()
        lexer = QsciLexerPython()
        tab.setLexer(lexer)
        tab.setText(text)
        tab.setMinimumSize(800, 600)  # 设置编辑区域的最小尺寸
        self.tabs.addTab(tab, title)

    # 设置代码补全
        self.setup_autocomplete(tab)

        tab = QsciScintilla()
        lexer = QsciLexerPython()
        tab.setLexer(lexer)
        tab.setText(text)
        self.tabs.addTab(tab, title)

        # 设置代码补全
        self.setup_autocomplete(tab)

    def setup_autocomplete(self, tab):
        # 设置补全源和阈值
        tab.setAutoCompletionSource(QsciScintilla.AcsAll)  # 使用所有的补全源
        tab.setAutoCompletionThreshold(1)  # 触发补全的阈值字符数

    def execute_command(self):
        command = self.console_input.text().strip()
        if command:
            self.console_output.append(f"$ {command}")
            try:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                self.console_output.append(stdout.decode())
                self.console_output.append(stderr.decode())
            except Exception as e:
                self.console_output.append(f"Error: {e}")

            self.console_input.clear()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #007ACC;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005EA6;
            }
            QTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #444;
            }
            QListWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
            }
            QDockWidget {
                background-color: #2E2E2E;
            }
        """)

    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        help_menu = menu_bar.addMenu("Help")

        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.prompt_open)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        file_menu.addAction(open_action)

        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.prompt_open_folder)
        file_menu.addAction(open_folder_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        file_menu.addAction(save_action)

    def prompt_open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Python File", "", "Python Files (*.py)")
        if file_path:
            self.open_file(file_path)

    def prompt_open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder_path:
            print(f"Selected folder: {folder_path}")  # 处理所选文件夹

    def open_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.add_new_tab(content, file_path.split('/')[-1])
        except Exception as e:
            self.statusBar().showMessage(f"Error reading file: {e}")

    def save_file(self):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Python File", "", "Python Files (*.py)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(current_tab.text())

    def load_user_preferences(self):
        try:
            with open("preferences.json", "r") as prefs_file:
                preferences = json.load(prefs_file)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PythonEditor()  
    editor.show()
    sys.exit(app.exec_())
