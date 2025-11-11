import sys
from PySide6.QtCore import QUrl, Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QMessageBox,
    QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QTabWidget
)
from PySide6.QtWebEngineWidgets import QWebEngineView


class PythonBrowser(QMainWindow):
    HOMEPAGE = QUrl("https://bonlop.pages.dev/")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Browser")
        self.setWindowIcon(QIcon())  # Optional: add custom icon file here

        # === Central Layout ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # === Tabs ===
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)
        layout.addWidget(self.tabs)

        # === Bookmarks Sidebar ===
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.setFixedWidth(140)
        self.bookmarks_list.itemDoubleClicked.connect(self.open_bookmark)
        layout.addWidget(self.bookmarks_list)

        # === Navigation Toolbar ===
        nav_bar = QToolBar("Navigation")
        nav_bar.setIconSize(QSize(20, 20))
        nav_bar.setMovable(False)
        self.addToolBar(nav_bar)
        self.add_nav_buttons(nav_bar)

        # === Menu Bar ===
        self.setup_menu()

        # === Initial Tab ===
        self.create_new_tab(self.HOMEPAGE)

        # === Styling ===
        self.apply_styles()
        self.showMaximized()

    # ---------------------------
    # Toolbar Buttons
    # ---------------------------
    def add_nav_buttons(self, nav_bar):
        btn_back = QAction("⬅️", self)
        btn_back.setStatusTip("Go back")
        btn_back.triggered.connect(lambda: self.browser_action("back"))
        nav_bar.addAction(btn_back)

        btn_forward = QAction("➡️", self)
        btn_forward.setStatusTip("Go forward")
        btn_forward.triggered.connect(lambda: self.browser_action("forward"))
        nav_bar.addAction(btn_forward)

        btn_reload = QAction("🔄", self)
        btn_reload.setStatusTip("Reload page")
        btn_reload.triggered.connect(lambda: self.browser_action("reload"))
        nav_bar.addAction(btn_reload)

        btn_home = QAction("🏠", self)
        btn_home.setStatusTip("Go to homepage")
        btn_home.triggered.connect(lambda: self.browser_action("home"))
        nav_bar.addAction(btn_home)

        nav_bar.addSeparator()

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL and press Enter...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        nav_bar.addSeparator()

        btn_bookmark = QAction("⭐", self)
        btn_bookmark.setStatusTip("Add Bookmark")
        btn_bookmark.triggered.connect(self.add_bookmark)
        nav_bar.addAction(btn_bookmark)

        btn_newtab = QAction("+", self)
        btn_newtab.setStatusTip("Open New Tab")
        btn_newtab.triggered.connect(self.confirm_add_new_tab)
        nav_bar.addAction(btn_newtab)

    # ---------------------------
    # Tab Management
    # ---------------------------
    def create_new_tab(self, url: QUrl):
        browser = QWebEngineView()
        browser.setUrl(url)
        index = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(index)

        # Update title and URL bar dynamically
        browser.titleChanged.connect(lambda title, br=browser: self.update_tab_title(br, title))
        browser.urlChanged.connect(lambda qurl: self.update_urlbar(qurl))
        browser.loadFinished.connect(lambda ok, br=browser: self.handle_load_finished(ok, br))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index >= 0:
            self.tabs.setTabText(index, title[:20] + ("…" if len(title) > 20 else ""))

    # ---------------------------
    # Navigation
    # ---------------------------
    def browser_action(self, action):
        browser = self.tabs.currentWidget()
        if not isinstance(browser, QWebEngineView):
            return

        match action:
            case "back":
                browser.back()
            case "forward":
                browser.forward()
            case "reload":
                browser.reload()
            case "home":
                browser.setUrl(self.HOMEPAGE)

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_urlbar(self, qurl=None):
        if not qurl and self.tabs.currentWidget():
            qurl = self.tabs.currentWidget().url()
        if qurl:
            self.url_bar.setText(qurl.toString())

    # ---------------------------
    # Bookmarks
    # ---------------------------
    def add_bookmark(self):
        browser = self.tabs.currentWidget()
        if isinstance(browser, QWebEngineView):
            url = browser.url().toString()
            title = browser.title() or url
            item = QListWidgetItem(QIcon(self.get_favicon(url)), title)
            item.setData(Qt.UserRole, url)
            self.bookmarks_list.addItem(item)

    def open_bookmark(self, item):
        url = item.data(Qt.UserRole)
        if url:
            self.tabs.currentWidget().setUrl(QUrl(url))

    def get_favicon(self, url):
        domain = QUrl(url).host()
        return f"https://{domain}/favicon.ico"

    # ---------------------------
    # Tabs and Loading
    # ---------------------------
    def confirm_add_new_tab(self):
        reply = QMessageBox.question(
            self, "Confirm", "Open a new tab? This may slow down the browser.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.create_new_tab(self.HOMEPAGE)

    def handle_load_finished(self, success, browser):
        if not success:
            QMessageBox.warning(self, "Load Error", "Failed to load the page. Returning to homepage.")
            browser.setUrl(self.HOMEPAGE)

    # ---------------------------
    # Menu
    # ---------------------------
    def setup_menu(self):
        menu = self.menuBar().addMenu("Options")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)

    def show_about(self):
        QMessageBox.information(
            self,
            "About Python Browser",
            "Python Browser v1.2\nBuilt with PySide6\nCreated by RobloxLiterature."
        )

    # ---------------------------
    # Styling
    # ---------------------------
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #20232a;
            }
            QToolBar {
                background-color: #2c313c;
                border: none;
                padding: 5px;
            }
            QLineEdit {
                background-color: #1e2127;
                color: #ffffff;
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #3e4451;
            }
            QLineEdit:focus {
                border: 1px solid #61afef;
            }
            QListWidget {
                background-color: #1e2127;
                color: #ffffff;
                border: none;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3e4451;
            }
            QMenuBar {
                background-color: #2c313c;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #3e4451;
            # }
            QMenu {
                background-color: #2c313c;
                color: white;
            }
            QMenu::item:selected {
                background-color: #3e4451;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PythonBrowser()
    window.show()
    sys.exit(app.exec())
