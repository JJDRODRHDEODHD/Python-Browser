import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QToolBar, QAction, QLineEdit, QMessageBox,
    QListWidget, QListWidgetItem, QWidget, QHBoxLayout, QTabWidget
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

class PythonBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Browser")

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Tab widget for managing multiple tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create the first tab
        self.create_new_tab(QUrl("http://www.google.com"))

        # Sidebar for bookmarks (thinner)
        self.bookmarks_list = QListWidget()
        self.layout.addWidget(self.bookmarks_list)
        self.bookmarks_list.setFixedWidth(100)  # Thinner sidebar

        # Navigation bar
        nav_bar = QToolBar("Navigation")
        self.addToolBar(nav_bar)

        # Back button
        back_btn = QAction("⬅️ Back", self)
        back_btn.triggered.connect(self.current_browser_back)
        nav_bar.addAction(back_btn)

        # Forward button
        forward_btn = QAction("➡️ Forward", self)
        forward_btn.triggered.connect(self.current_browser_forward)
        nav_bar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction("🔄 Reload", self)
        reload_btn.triggered.connect(self.current_browser_reload)
        nav_bar.addAction(reload_btn)

        # Home button
        home_btn = QAction("🏠 Home", self)
        home_btn.triggered.connect(self.current_browser_home)
        nav_bar.addAction(home_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        # Add bookmark button
        bookmark_btn = QAction("⭐ Bookmark", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        nav_bar.addAction(bookmark_btn)

        # Add new tab button
        add_tab_btn = QAction("+", self)
        add_tab_btn.triggered.connect(self.confirm_add_new_tab)
        nav_bar.addAction(add_tab_btn)

        # Update URL bar when the page changes
        self.tabs.currentChanged.connect(self.update_urlbar)

        # Options menu
        options_menu = self.menuBar().addMenu("Options")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        options_menu.addAction(about_action)

        self.showMaximized()

        # Custom styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #282c34; /* Dark background */
            }
            QToolBar {
                background-color: #3e4451; /* Toolbar background */
            }
            QLineEdit {
                background-color: #1e2127; /* URL bar background */
                color: white; /* Text color */
                padding: 5px; /* Padding */
            }
            QLineEdit:focus {
                background-color: #3e4451; /* Change on focus */
            }
            QAction {
                color: white; /* Button text color */
                padding: 10px; /* Button padding */
            }
            QMenuBar {
                background-color: #3e4451; /* Menu bar background */
            }
            QMenu {
                background-color: #3e4451; /* Menu background */
                color: white; /* Menu text color */
                border: none; /* No border */
            }
            QMenu::item:selected {
                background-color: #50555b; /* Highlighted menu item */
            }
            QListWidget {
                background-color: #1e2127; /* Bookmarks background */
                color: white; /* Bookmarks text color */
                border: none; /* No border */
            }
            QListWidget::item:selected {
                background-color: #50555b; /* Highlighted bookmark */
            }
        """)

    def create_new_tab(self, url):
        new_tab = QWebEngineView()
        new_tab.setUrl(url)
        self.tabs.addTab(new_tab, url.toString())

        # Connect the URL bar to the new tab's URL
        new_tab.urlChanged.connect(lambda qurl: self.update_urlbar(qurl))
        new_tab.loadFinished.connect(lambda success: self.on_load_finished(success, new_tab))

    def on_load_finished(self, success, tab):
        if not success:
            QMessageBox.warning(self, "Loading Error", "Failed to load the page.")
            tab.setUrl(QUrl("http://www.google.com"))  # Fallback to homepage on error

    def confirm_add_new_tab(self):
        reply = QMessageBox.question(
            self,
            'Confirm Open Tab',
            "Are you sure you want to do this? It might crash the browser.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.add_new_tab()

    def add_new_tab(self):
        self.create_new_tab(QUrl("http://www.google.com"))

    def current_browser_back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()

    def current_browser_forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()

    def current_browser_reload(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()

    def current_browser_home(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        current_browser = self.tabs.currentWidget()
        if current_browser:
            # Try to set the URL, handle any exceptions
            try:
                current_browser.setUrl(QUrl(url))
            except Exception as e:
                QMessageBox.warning(self, "Invalid URL", str(e))

    def update_urlbar(self, qurl):
        self.url_bar.setText(qurl.toString())

    def add_bookmark(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_url = current_browser.url().toString()
            if current_url:
                icon_url = self.get_favicon(current_url)
                item = QListWidgetItem(QIcon(icon_url), current_url)
                self.bookmarks_list.addItem(item)

    def get_favicon(self, url):
        domain = QUrl(url).host()
        favicon_url = f"https://{domain}/favicon.ico"
        return favicon_url  # Return URL directly for the icon

    def show_about(self):
        QMessageBox.information(self, "About", "Python Browser\nVersion 1.0\nCreated by RobloxLiterature.")

app = QApplication(sys.argv)
browser_window = PythonBrowser()
browser_window.showMaximized()
sys.exit(app.exec_())
