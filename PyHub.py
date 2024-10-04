import sys
import json
import subprocess
import webbrowser
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget, QPushButton,
    QTextEdit, QAction, QStatusBar, QTabWidget, QDialog, QLineEdit, QListWidget,
    QDockWidget, QInputDialog, QLabel, QHBoxLayout, QMessageBox
)
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtCore import Qt, QProcess, QTimer


# 文件浏览器类，继承自QDockWidget，用户可以通过它浏览当前目录中的Python文件
class FileBrowser(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Browser")  # 设置窗口标题为 "File Browser"
        self.setGeometry(300, 100, 200, 400)  # 设置窗口大小和位置
        self.current_directory = '.'  # 初始化当前目录为当前路径

        # 创建显示文件列表的 QListWidget
        self.file_list_widget = QListWidget()
        # 双击文件时，调用open_selected_file方法打开该文件
        self.file_list_widget.itemDoubleClicked.connect(self.open_selected_file)

        # 添加一个按钮，允许用户返回上一级目录
        self.up_button = QPushButton("Up", self)
        self.up_button.clicked.connect(self.go_up_directory)

        # 设置布局，将按钮和文件列表添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(self.up_button)
        layout.addWidget(self.file_list_widget)

        # 创建一个容器以设置布局
        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)

        self.load_files()  # 加载当前目录下的文件

    # 加载当前目录下的所有.py文件
    def load_files(self):
        import os
        self.file_list_widget.clear()  # 清空文件列表
        try:
            # 遍历当前目录中的文件，只显示.py文件
            for file in os.listdir(self.current_directory):
                if file.endswith('.py'):
                    self.file_list_widget.addItem(file)
        except Exception as e:
            # 如果加载失败，显示错误信息
            QMessageBox.critical(self, "Error", f"Failed to load directory:\n{e}")

    # 设置浏览器的当前目录
    def set_directory(self, directory):
        self.current_directory = directory
        self.load_files()  # 加载该目录下的文件

    # 打开选中的文件
    def open_selected_file(self, item):
        file_path = os.path.join(self.current_directory, item.text())  # 获取文件的完整路径
        self.parent().open_file(file_path)  # 通过父类的open_file方法打开文件

    # 返回上一级目录
    def go_up_directory(self):
        import os
        parent_dir = os.path.dirname(os.path.abspath(self.current_directory))  # 获取上一级目录路径
        self.set_directory(parent_dir)  # 设置为上一级目录，并重新加载文件列表


# 代码片段管理器类，继承自QDialog，用于管理用户自定义的代码片段
class SnippetManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Code Snippets")  # 设置窗口标题
        self.setGeometry(100, 100, 300, 400)  # 设置窗口大小和位置

        # 创建代码片段列表
        self.snippets_list = QListWidget(self)
        self.load_snippets()  # 加载默认的代码片段

        # 添加片段按钮，点击时调用add_snippet方法
        add_button = QPushButton("Add Snippet", self)
        add_button.clicked.connect(self.add_snippet)

        # 编辑片段按钮，点击时调用edit_snippet方法
        edit_button = QPushButton("Edit Snippet", self)
        edit_button.clicked.connect(self.edit_snippet)

        # 删除片段按钮，点击时调用delete_snippet方法
        delete_button = QPushButton("Delete Snippet", self)
        delete_button.clicked.connect(self.delete_snippet)

        # 布局，将按钮和列表添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(self.snippets_list)
        layout.addWidget(add_button)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        self.setLayout(layout)

    # 加载默认的代码片段
    def load_snippets(self):
        self.snippets_list.addItems([
            "print('Hello, World!')",
            "for i in range(10):",
            "if __name__ == '__main__':"
        ])

    # 添加新的代码片段
    def add_snippet(self):
        new_snippet, ok = QInputDialog.getText(self, "Add Snippet", "Snippet:")  # 弹出输入对话框
        if ok and new_snippet:
            self.snippets_list.addItem(new_snippet)  # 将新片段添加到列表中

    # 编辑选中的代码片段
    def edit_snippet(self):
        item = self.snippets_list.currentItem()  # 获取当前选中的片段
        if item:
            new_snippet, ok = QInputDialog.getText(
                self, "Edit Snippet", "Edit your snippet:", text=item.text()
            )
            if ok and new_snippet:
                item.setText(new_snippet)  # 更新片段内容

    # 删除选中的代码片段
    def delete_snippet(self):
        item = self.snippets_list.currentItem()  # 获取当前选中的片段
        if item:
            self.snippets_list.takeItem(self.snippets_list.row(item))  # 删除该片段


# 资源管理器类，继承自QDockWidget，用于管理项目中的资源文件
class ResourceManager(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Resource Manager")  # 设置窗口标题
        self.setGeometry(400, 100, 250, 400)  # 设置窗口大小和位置

        self.resource_list = QListWidget(self)  # 创建资源列表
        self.load_resources()  # 加载示例资源

        self.setWidget(self.resource_list)  # 设置资源列表为DockWidget的主部件

    # 加载示例资源
    def load_resources(self):
        self.resource_list.addItems(["image1.png", "style.css", "script.js"])  # 示例资源


# 任务管理器类，继承自QDockWidget，用于管理任务列表
class TaskManager(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Manager")  # 设置窗口标题
        self.setGeometry(600, 100, 300, 400)  # 设置窗口大小和位置

        self.task_list = QListWidget()  # 创建任务列表
        self.add_task_button = QPushButton("Add Task", self)  # 添加任务按钮
        self.add_task_button.clicked.connect(self.add_task)  # 按钮点击时，添加任务

        # 设置布局，将任务列表和添加按钮放入布局
        layout = QVBoxLayout()
        layout.addWidget(self.task_list)
        layout.addWidget(self.add_task_button)

        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)

    # 添加任务
    def add_task(self):
        task_text, ok = QInputDialog.getText(self, "New Task", "Task description:")  # 弹出输入框
        if ok and task_text:
            self.task_list.addItem(task_text)  # 将任务添加到任务列表中


# 查找替换对话框，继承自QDialog，允许用户查找和替换代码中的文本
class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor  # 保存传入的编辑器实例，QsciScintilla
        self.setWindowTitle("Find and Replace")  # 设置窗口标题
        self.setGeometry(300, 300, 400, 150)  # 设置窗口大小和位置

        # 创建查找和替换输入框
        find_label = QLabel("Find:")
        self.find_input = QLineEdit()
        replace_label = QLabel("Replace:")
        self.replace_input = QLineEdit()

        # 匹配大小写按钮
        self.case_checkbox = QPushButton("Match Case")
        self.case_checkbox.setCheckable(True)  # 使按钮可切换

        # 查找、替换和全部替换按钮
        find_button = QPushButton("Find")
        find_button.clicked.connect(self.find_text)
        replace_button = QPushButton("Replace")
        replace_button.clicked.connect(self.replace_text)
        replace_all_button = QPushButton("Replace All")
        replace_all_button.clicked.connect(self.replace_all_text)

        # 设置布局
        layout = QVBoxLayout()

        # 查找输入框布局
        find_layout = QHBoxLayout()
        find_layout.addWidget(find_label)
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)

        # 替换输入框布局
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)

        # 选项布局
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.case_checkbox)
        layout.addLayout(options_layout)

        # 按钮布局
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(find_button)
        buttons_layout.addWidget(replace_button)
        buttons_layout.addWidget(replace_all_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    # 查找文本
    def find_text(self):
        find_str = self.find_input.text()  # 获取查找文本
        if not find_str:
            return

        # 判断是否匹配大小写
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
            QMessageBox.information(self, "Find", f"'{find_str}' not found.")  # 未找到时提示

    # 替换文本
    def replace_text(self):
        find_str = self.find_input.text()  # 获取查找文本
        replace_str = self.replace_input.text()  # 获取替换文本
        if not find_str:
            return

        # 获取当前光标选中的文本并进行替换
        cursor = self.editor.textCursor()
        selected_text = self.editor.selectedText()
        if (self.case_checkbox.isChecked() and selected_text == find_str) or \
           (not self.case_checkbox.isChecked() and selected_text.lower() == find_str.lower()):
            self.editor.replaceSelectedText(replace_str)

        # 查找下一个匹配项
        self.find_text()

    # 替换所有匹配的文本
    def replace_all_text(self):
        find_str = self.find_input.text()  # 获取查找文本
        replace_str = self.replace_input.text()  # 获取替换文本
        if not find_str:
            return

        # 保存当前光标位置
        current_pos = self.editor.getCursorPosition()

        self.editor.beginUndoAction()
        self.editor.setCursorPosition(0, 0)
        replaced = 0  # 记录替换次数
        while self.editor.findFirst(
            find_str,
            False,
            self.case_checkbox.isChecked(),
            False,
            False,
            True
        ):
            self.editor.replaceSelectedText(replace_str)
            replaced += 1  # 每次替换后计数
        self.editor.endUndoAction()

        # 显示替换结果
        QMessageBox.information(self, "Replace All", f"Replaced {replaced} occurrences.")

        # 恢复光标位置
        self.editor.setCursorPosition(*current_pos)

#主题切换
class ThemeSwitcher(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Switcher")  # 设置窗口标题
        self.setGeometry(500, 300, 200, 100)  # 设置窗口大小和位置
        # 创建主题列表
        self.theme_list = QListWidget(self)
        self.theme_list.addItems(["Default", "Dark", "Light"])

        # 切换按钮
        self.switch_button = QPushButton("Switch", self)
        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.theme_list)
        layout.addWidget(self.switch_button)
        self.setLayout(layout)

        # 切换按钮点击事件
        self.switch_button.clicked.connect(self.apply_theme)

    def apply_theme(self):
        selected_theme = self.theme_list.currentItem().text()  # 获取当前选中的主题
        if selected_theme == "Dark":
            self.parent().setStyleSheet("background-color: #2E2E2E; color: white;")
        elif selected_theme == "Light":
            self.parent().setStyleSheet("background-color: white; color: black;")
        else:
            self.parent().setStyleSheet("""
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
        """)  # 默认样式
        self.close()  # 关闭窗口

# Python 编辑器主窗口类，继承自QMainWindow
class PythonEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('icon.png'))  # 设置窗口图标
        self.setWindowTitle("PyHub")  # 设置窗口标题
        self.setGeometry(100, 100, 1000, 700)  # 设置窗口大小

        self.apply_styles()  # 应用样式
        self.tabs = QTabWidget()  # 创建标签页组件
        self.tabs.setTabsClosable(True)  # 启用关闭按钮
        self.tabs.tabCloseRequested.connect(self.close_tab)  # 连接关闭标签页事件
        self.setCentralWidget(self.tabs)  # 将标签页设置为主窗口的中央部件
        self.add_new_tab()  # 添加一个新标签页

        # 控制台输出显示框
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)  # 设置为只读
        self.console_output.setStyleSheet("background-color: black; color: white;")  # 设置样式

        # 控制台输入框
        self.console_input = QLineEdit()
        self.console_input.setPlaceholderText("Enter command here...")  # 设置占位文本

        # 运行按钮
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_code)  # 连接到运行代码的方法

        # 停止按钮，初始隐藏
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_code)
        self.stop_button.setVisible(False)  # 隐藏停止按钮

        # 设置控制台布局
        console_layout = QVBoxLayout()
        console_layout.addWidget(run_button)
        console_layout.addWidget(self.stop_button)
        console_layout.addWidget(self.console_output)
        console_layout.addWidget(self.console_input)

        console_container = QWidget()
        console_container.setLayout(console_layout)

        # 将控制台设置为底部停靠窗口
        self.console_dock = QDockWidget("Console", self)
        self.console_dock.setWidget(console_container)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        # 文件浏览器
        self.file_browser = FileBrowser(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_browser)

        # 资源管理器
        self.resource_manager = ResourceManager(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.resource_manager)

        # 任务管理器
        self.task_manager = TaskManager(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.task_manager)

        self.create_menu()  # 创建菜单栏
        self.load_user_preferences()  # 加载用户偏好设置

        # 自动保存功能，设置每30秒保存一次
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(30000)

        # 当用户在控制台输入命令时，执行命令
        self.console_input.returnPressed.connect(self.execute_command)

        # 使用QProcess来运行外部Python脚本
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

    # 关闭标签页
    def close_tab(self, index):
        if index >= 0:
            current_tab = self.tabs.widget(index)  # 获取要关闭的标签页
            if current_tab:
                self.tabs.removeTab(index)  # 从标签页中移除该标签页
                current_tab.deleteLater()  # 删除该部件

    # 运行当前代码
    def run_code(self):
        current_tab = self.tabs.currentWidget()  # 获取当前标签页
        if isinstance(current_tab, QsciScintilla):
            code = current_tab.text()  # 获取代码文本
            with open('temp_script.py', 'w', encoding='utf-8') as script_file:
                script_file.write(code)  # 将代码保存到临时文件中

            self.stop_button.setVisible(True)  # 显示停止按钮
            self.statusBar().showMessage("Code is running...")  # 更新状态栏信息

            # 使用QProcess运行Python脚本
            self.process.start('python', ['temp_script.py'])

    # 停止正在运行的代码
    def stop_code(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()  # 终止正在运行的进程
            self.console_output.append("Code execution stopped.")  # 控制台输出停止信息
            self.stop_button.setVisible(False)  # 隐藏停止按钮
            self.statusBar().showMessage("Code execution stopped.")  # 更新状态栏信息

    # 处理标准输出
    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self.console_output.append(str(data, encoding='utf-8'))  # 将标准输出添加到控制台

    # 处理标准错误
    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self.console_output.append(str(data, encoding='utf-8'))  # 将错误输出添加到控制台

    # 进程完成后调用
    def process_finished(self):
        self.stop_button.setVisible(False)  # 隐藏停止按钮
        self.statusBar().showMessage("Code execution finished.")  # 更新状态栏信息

    # 自动保存当前文件
    def auto_save(self):
        current_tab = self.tabs.currentWidget()  # 获取当前标签页
        if isinstance(current_tab, QsciScintilla):
            file_name = self.tabs.tabText(self.tabs.currentIndex())  # 获取文件名
            if file_name and file_name != "新建文件":  # 检查文件名是否有效
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(current_tab.text())  # 保存文件
                self.statusBar().showMessage(f"Autosaved: {file_name}")  # 更新状态栏信息

    # 添加新的标签页
    def add_new_tab(self, text='', title='新建文件'):
        tab = QsciScintilla()
        lexer = QsciLexerPython()

        # 设置不同类型的高亮颜色
        lexer.setColor(QColor('#1165e4'), QsciLexerPython.Keyword)   # 关键字
        lexer.setColor(QColor('#11e460'), QsciLexerPython.Comment)  # 注释
        lexer.setColor(QColor('#de8a02'), 2)                         # 字符串 (通常在 QScintilla 中对应的索引)
        lexer.setColor(QColor("#9006cb"), 3)                       # 数字 (通常在 QScintilla 中对应的索引)

        tab.setLexer(lexer)
        tab.setText(text)
        tab.setMinimumSize(800, 600)
        #设置字体
        font = QFont("Segoe UI", 10, QFont.Normal)  # 指定字体名称、字号和样式
        tab.setFont(font)
        self.tabs.addTab(tab, title)

        # 设置代码补全
        self.setup_autocomplete(tab)

        tab = QsciScintilla()  # 创建新的编辑器
        lexer = QsciLexerPython()  # 使用Python语法高亮
        tab.setLexer(lexer)
        tab.setText(text)  # 设置初始文本
        tab.setMinimumSize(800, 600)  # 设置编辑器最小大小
        self.tabs.addTab(tab, title)  # 添加标签页

        # 设置代码补全功能
        self.setup_autocomplete(tab)

    # 设置自动补全
    def setup_autocomplete(self, tab):
        tab.setAutoCompletionSource(QsciScintilla.AcsAll)  # 使用所有补全来源
        tab.setAutoCompletionThreshold(1)  # 设置触发补全的阈值

    # 执行命令行命令
    def execute_command(self):
        command = self.console_input.text().strip()  # 获取输入的命令
        if command:
            self.console_output.append(f"$ {command}")  # 在控制台输出命令
            try:
                # 使用subprocess执行命令
                process = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                self.console_output.append(stdout.decode())  # 输出标准输出
                self.console_output.append(stderr.decode())  # 输出错误信息
            except Exception as e:
                self.console_output.append(f"Error: {e}")  # 捕获异常并输出错误

            self.console_input.clear()  # 清空输入框

    # 应用样式
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

    # 创建菜单栏
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        help_menu = menu_bar.addMenu("Help")

        # 打开文件动作
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.prompt_open)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        file_menu.addAction(open_action)

        # 打开文件夹动作
        open_folder_action = QAction("Open Folder", self)
        open_folder_action.triggered.connect(self.prompt_open_folder)
        file_menu.addAction(open_folder_action)

        # 保存文件动作
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        file_menu.addAction(save_action)
        
        # 注入代码动作
        inject_action = QAction("Inject Code", self)
        inject_action.triggered.connect(self.prompt_inject_code)  # 设置注入代码对话框
        edit_menu.addAction(inject_action)

        # 查找和替换动作
        find_action = QAction("Find", self)
        find_action.triggered.connect(self.open_find_dialog)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        edit_menu.addAction(find_action)

        replace_action = QAction("Replace", self)
        replace_action.triggered.connect(self.open_replace_dialog)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        edit_menu.addAction(replace_action)
    def inject_code(self, code):
        # 检查是否为空
        if not code.strip():
            QMessageBox.warning(self, "Warning", "No code to inject.")
            return
        
        # 创建一个临时文件来保存注入的代码
        with open('injected_code.py', 'w', encoding='utf-8') as inject_file:
            inject_file.write(code)

        # 使用QProcess执行注入的代码
        self.process.start('python', ['injected_code.py'])

    # 运行当前代码的方法，决定是否允许用户注入代码
    def run_code(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            code = current_tab.text()
            # 这里可以选择是否运行当前代码或仅执行注入代码

            with open('temp_script.py', 'w', encoding='utf-8') as script_file:
                script_file.write(code)

            self.stop_button.setVisible(True)
            self.statusBar().showMessage("Code is running...")

            self.process.start('python', ['temp_script.py'])

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

        # 注入代码动作
        inject_action = QAction("Inject Code", self)
        inject_action.triggered.connect(self.prompt_inject_code)  # 设定触发注入的方法
        edit_menu.addAction(inject_action)

        find_action = QAction("Find", self)
        find_action.triggered.connect(self.open_find_dialog)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        edit_menu.addAction(find_action)

        replace_action = QAction("Replace", self)
        replace_action.triggered.connect(self.open_replace_dialog)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        edit_menu.addAction(replace_action)
        
        #主题切换
        documentation_action = QAction("topic", self)
        documentation_action.triggered.connect(self.topic)
        edit_menu.addAction(documentation_action)

        #帮助文档
        documentation_action = QAction("Help documentation", self)
        documentation_action.triggered.connect(self.Help_documentation)
        help_menu.addAction(documentation_action)

    # 弹出对话框让用户输入要注入的代码
    def prompt_inject_code(self):
        code, ok = QInputDialog.getText(self, "Inject Custom Code", "Enter your code:")
        if ok and code:
            self.inject_code(code)  # 进行代码注入

        

    # 提示打开文件
    def prompt_open(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Python File", "", "Python Files (*.py)"
        )
        if file_path:
            self.open_file(file_path)

    # 提示打开文件夹
    def prompt_open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", "")
        if folder_path:
            self.file_browser.set_directory(folder_path)

    # 打开文件
    def open_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.add_new_tab(content, os.path.basename(file_path))  # 将内容添加到新标签页中
        except Exception as e:
            self.statusBar().showMessage(f"Error reading file: {e}")

    # 保存文件
    def save_file(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Python File", "", "Python Files (*.py)"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(current_tab.text())  # 保存当前代码
                    self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(file_path))  # 更新标签页标题
                    self.statusBar().showMessage(f"Saved: {file_path}")  # 更新状态栏信息
                except Exception as e:
                    self.statusBar().showMessage(f"Error saving file: {e}")

    # 加载用户偏好设置
    def load_user_preferences(self):
        try:
            with open("preferences.json", "r") as prefs_file:
                preferences = json.load(prefs_file)
                # 根据需要应用用户偏好设置
        except FileNotFoundError:
            pass

    # 打开查找对话框
    def open_find_dialog(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            self.find_dialog = FindReplaceDialog(current_tab, self)
            self.find_dialog.show()

    # 打开替换对话框
    def open_replace_dialog(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            self.replace_dialog = FindReplaceDialog(current_tab, self)
            self.replace_dialog.show()

    # 弹出对话框让用户输入要注入的代码
    def prompt_inject_code(self):
        code, ok = QInputDialog.getText(self, "Inject Custom Code", "Enter your code:")
        if ok and code:
            self.inject_code(code)  # 注入用户输入的代码
    


    # 帮助文档
    def Help_documentation(self):
        webbrowser.open("https://e0ds3o5azc.feishu.cn/docx/TyozdBek4oTnZvxJFqQceG3vnxb?from=from_copylink")

    # 主题切换
    def topic(self):
        current_tab = self.tabs.currentWidget()
        if isinstance(current_tab, QsciScintilla):
            self.theme_switcher = ThemeSwitcher(self)
            self.theme_switcher.show()


if __name__ == "__main__":
    import os
    app = QApplication(sys.argv)
    editor = PythonEditor()
    editor.show()
    sys.exit(app.exec_())