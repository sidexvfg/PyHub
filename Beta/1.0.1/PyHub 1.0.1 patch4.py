import sys
import json
import subprocess
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QPushButton,
    QTextEdit, QAction, QStatusBar, QTabWidget, QDialog, QLineEdit, QListWidget,
    QDockWidget, QInputDialog, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtCore import Qt, QProcess, QTimer


class FileBrowser(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Browser")
        self.setGeometry(300, 100, 200, 400)
        self.current_directory = '.'  # Initialize with current directory

        self.file_list_widget = QListWidget()
        self.file_list_widget.itemDoubleClicked.connect(self.open_selected_file)

        # Add a button to go up one directory
        self.up_button = QPushButton("Up", self)
        self.up_button.clicked.connect(self.go_up_directory)

        # Layout for the dock widget
        layout = QVBoxLayout()
        layout.addWidget(self.up_button)
        layout.addWidget(self.file_list_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)

        self.load_files()

    def load_files(self):
        import os
        self.file_list_widget.clear()
        try:
            for file in os.listdir(self.current_directory):
                if file.endswith('.py'):
                    self.file_list_widget.addItem(file)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load directory:\n{e}")

    def set_directory(self, directory):
        self.current_directory = directory
        self.load_files()

    def open_selected_file(self, item):
        file_path = os.path.join(self.current_directory, item.text())
        self.parent().open_file(file_path)

    def go_up_directory(self):
        import os
        parent_dir = os.path.dirname(os.path.abspath(self.current_directory))
        self.set_directory(parent_dir)


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
            new_snippet, ok = QInputDialog.getText(
                self, "Edit Snippet", "Edit your snippet:", text=item.text()
            )
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


class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor  # QsciScintilla instance
        self.setWindowTitle("Find and Replace")
        self.setGeometry(300, 300, 400, 150)

        # Widgets
        find_label = QLabel("Find:")
        self.find_input = QLineEdit()
        replace_label = QLabel("Replace:")
        self.replace_input = QLineEdit()

        self.case_checkbox = QPushButton("Match Case")
        self.case_checkbox.setCheckable(True)

        find_button = QPushButton("Find")
        find_button.clicked.connect(self.find_text)
        replace_button = QPushButton("Replace")
        replace_button.clicked.connect(self.replace_text)
        replace_all_button = QPushButton("Replace All")
        replace_all_button.clicked.connect(self.replace_all_text)

        # Layouts
        layout = QVBoxLayout()

        find_layout = QHBoxLayout()
        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)

        replace_layout = QHBoxLayout()
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)

        options_layout = QHBoxLayout()
        options_layout.addWidget(self.case_checkbox)
        layout.addLayout(options_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(find_button)
        buttons_layout.addWidget(replace_button)
        buttons_layout.addWidget(replace_all_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def find_text(self):
        find_str = self.find_input.text()
        if not find_str:
            return

        flags = QsciScintilla.SCFIND_MATCHCASE if self.case_checkbox.isChecked() else 0
        pos = self.editor.findFirst(
            find_str,
            False,
            self.case_checkbox.isChecked(),
            False,
            False,
            True
        )
        if not pos:
            QMessageBox.information(self, "Find", f"'{find_str}' not found.")

    def replace_text(self):
        find_str = self.find_input.text()
        replace_str = self.replace_input.text()
        if not find_str:
            return

        cursor = self.editor.textCursor()
        selected_text = self.editor.selectedText()
        if (self.case_checkbox.isChecked() and selected_text == find_str) or \
           (not self.case_checkbox.isChecked() and selected_text.lower() == find_str.lower()):
            self.editor.replaceSelectedText(replace_str)

        self.find_text()

    def replace_all_text(self):
        find_str = self.find_input.text()
        replace_str = self.replace_input.text()
        if not find_str:
            return

        # Save current cursor position
        current_pos = self.editor.getCursorPosition()

        self.editor.beginUndoAction()
        self.editor.setCursorPosition(0, 0)
        replaced = 0
        while self.editor.findFirst(
            find_str,
            False,
            self.case_checkbox.isChecked(),
            False,
            False,
            True
        ):
            self.editor.replaceSelectedText(replace_str)
            replaced += 1
        self.editor.endUndoAction()

        QMessageBox.information(self, "Replace All", f"Replaced {replaced} occurrences.")

        # Restore cursor position
        self.editor.setCursorPosition(*current_pos)


class PythonEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowTitle("PyHub")
        self.setGeometry(100, 100, 1000, 700)  # Increased width for better layout

        self.apply_styles()
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)  # Enable close buttons
        self.tabs.tabCloseRequested.connect(self.close_tab)  # Connect close event
        self.setCentralWidget(self.tabs)
        self.add_new_tab()

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("background-color: black; color: white;")

        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("Enter command here...")

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_code)  # Connect to run_code method

        # Add Stop button
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_code)
        self.stop_button.setVisible(False)  # Initially hidden

        # Layout for console and buttons
        console_layout = QVBoxLayout()
        console_layout.addWidget(run_button)
        console_layout.addWidget(self.stop_button)
        console_layout.addWidget(self.console_output)
        console_layout.addWidget(self.console_input)

        console_container = QWidget()
        console_container.setLayout(console_layout)

        # Dock for the console at the bottom
        self.console_dock = QDockWidget("Console", self)
        self.console_dock.setWidget(console_container)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        self.file_browser = FileBrowser(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_browser)

        self.resource_manager = ResourceManager(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.resource_manager)

        self.task_manager = TaskManager(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.task_manager)

        self.create_menu()
        self.load_user_preferences()

        # Use QTimer for auto-save
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)  # Run every 30 seconds

        self.console_input.returnPressed.connect(self.execute_command)

        # QProcess for running scripts
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    def close_tab(self, index):
        """Close the tab at the given index"""
        if index >= 0:
            current_tab = self.tabs.widget(index)
            if current_tab:
                self.tabs.removeTab(index)
                current_tab.deleteLater()  # Delete the widget of the tab

    def run_code(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            code = current_tab.text()
            with open('temp_script.py', 'w', encoding='utf-8') as script_file:
                script_file.write(code)

            self.stop_button.setVisible(True)
            self.statusBar().showMessage("Code is running...")

            # Start QProcess to run the code
            self.process.start('python', ['temp_script.py'])

    def stop_code(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()  # Terminate the running process
            self.console_output.append("Code execution stopped.")
            self.stop_button.setVisible(False)  # Hide Stop button
            self.statusBar().showMessage("Code execution stopped.")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.console_output.append(str(data, encoding='utf-8'))

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.console_output.append(str(data, encoding='utf-8'))

    def process_finished(self):
        self.stop_button.setVisible(False)  # Hide Stop button
        self.statusBar().showMessage("Code execution finished.")

    def auto_save(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            file_name = self.tabs.tabText(self.tabs.currentIndex())
            # Check if the file name is valid
            if file_name and file_name != "新建文件":
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(current_tab.text())
                self.statusBar().showMessage(f"Autosaved: {file_name}")

    def add_new_tab(self, text='', title='新建文件'):
        tab = QsciScintilla()
        lexer = QsciLexerPython()
        tab.setLexer(lexer)
        tab.setText(text)
        tab.setMinimumSize(800, 600)  # Set minimum size of editor area
        self.tabs.addTab(tab, title)

        # Set code completion
        self.setup_autocomplete(tab)

    def setup_autocomplete(self, tab):
        # Set the auto-completion source and threshold
        tab.setAutoCompletionSource(QsciScintilla.AcsAll)  # Use all completion sources
        tab.setAutoCompletionThreshold(1)  # Threshold for triggering auto-completion

    def execute_command(self):
        command = self.console_input.text().strip()
        if command:
            self.console_output.append(f"$ {command}")
            try:
                process = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
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
            QLineEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #444;
                padding: 5px;
            }
            QTabWidget::pane { /* The tab widget frame */
                border-top: 2px solid #C2C7CB;
            }
            QTabBar::tab {
                background: #2E2E2E;
                color: white;
                padding: 10px;
                border: 1px solid #444;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #1E1E1E;
                border-bottom: 2px solid #1E1E1E;
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

        # Find and Replace actions
        find_action = QAction("Find", self)
        find_action.triggered.connect(self.open_find_dialog)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        edit_menu.addAction(find_action)

        replace_action = QAction("Replace", self)
        replace_action.triggered.connect(self.open_replace_dialog)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        edit_menu.addAction(replace_action)

    def prompt_open(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Python File", "", "Python Files (*.py)"
        )
        if file_path:
            self.open_file(file_path)

    def prompt_open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder_path:
            self.file_browser.set_directory(folder_path)

    def open_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.add_new_tab(content, os.path.basename(file_path))
        except Exception as e:
            self.statusBar().showMessage(f"Error reading file: {e}")

    def save_file(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Python File", "", "Python Files (*.py)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(current_tab.text())
                    self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))
                    self.statusBar().showMessage(f"Saved: {file_path}")
                except Exception as e:
                    self.statusBar().showMessage(f"Error saving file: {e}")

    def load_user_preferences(self):
        try:
            with open("preferences.json", "r") as prefs_file:
                preferences = json.load(prefs_file)
                # Apply preferences as needed
        except FileNotFoundError:
            pass

    def open_find_dialog(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            self.find_dialog = FindReplaceDialog(current_tab, self)
            self.find_dialog.show()

    def open_replace_dialog(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            self.replace_dialog = FindReplaceDialog(current_tab, self)
            self.replace_dialog.show()


if __name__ == "__main__":
    import os
    app = QApplication(sys.argv)
    editor = PythonEditor()
    editor.show()
    sys.exit(app.exec_())
