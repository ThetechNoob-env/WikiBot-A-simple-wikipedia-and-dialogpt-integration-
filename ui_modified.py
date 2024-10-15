from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QHBoxLayout, QTextEdit, QComboBox, QApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize
import os
import sys
from wiki_modified import WikipediaHandler
from dialogpt import DialogPTHandler

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

class WikiBotUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize Wikipedia and DialogPT handlers
        self.wikipedia_handler = WikipediaHandler()
        self.dialogpt_handler = DialogPTHandler()
        self.current_source = "Wikipedia"  # Default to Wikipedia
        self.is_dark_mode = True  # Start with dark mode by default
        self.summary_type = "Medium"  # Set default summary type

        self.initUI()

    def initUI(self):
        """Set up the main UI components."""
        self.setWindowTitle("WikiBot - A Simple Wikipedia Assistant")
        self.setGeometry(100, 100, 900, 700)

        # Set up the central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Title label
        self.title_label = QLabel("WikiBot AI Assistant", self)
        self.title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Add the logo
        self.logo = QLabel(self)
        self.logo.setPixmap(QIcon(resource_path("icon.png")).pixmap(QSize(100, 100)))
        self.logo.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.logo)

        # Search bar with icon
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Enter a topic to search...")
        self.search_bar.setFont(QFont("Arial", 16))
        self.search_bar.setStyleSheet(self.search_bar_style())

        search_layout.addWidget(self.search_bar)
        self.layout.addLayout(search_layout)

        # Source selector (Dropdown or ComboBox)
        self.source_selector = QComboBox(self)
        self.source_selector.setFont(QFont("Arial", 14))
        self.source_selector.addItem("Wikipedia")
        self.source_selector.addItem("DialogPT")
        self.source_selector.currentIndexChanged.connect(self.change_source)
        self.layout.addWidget(self.source_selector)

        # Summary options dropdown
        self.summary_selector = QComboBox(self)
        self.summary_selector.setFont(QFont("Arial", 14))
        self.summary_selector.addItem("Medium")
        self.summary_selector.addItem("Detailed")
        self.summary_selector.currentIndexChanged.connect(lambda index: self.set_summary_type(self.summary_selector.itemText(index)))
        self.layout.addWidget(self.summary_selector)

        # Search button
        self.search_button = QPushButton("Search", self)
        self.search_button.setFont(QFont("Arial", 16))
        self.search_button.setStyleSheet(self.button_style())
        self.search_button.clicked.connect(self.perform_search)
        self.layout.addWidget(self.search_button)

        # Add output area
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Arial", 14))
        self.output_area.setStyleSheet(self.output_area_style())
        self.layout.addWidget(self.output_area)

        # Source reference label
        self.source_reference_label = QLabel("", self)
        self.source_reference_label.setFont(QFont("Arial", 12))
        self.source_reference_label.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.source_reference_label)

        # Dark Mode toggle button
        self.theme_toggle = QPushButton("Switch to Light Mode", self)
        self.theme_toggle.setFont(QFont("Arial", 14))
        self.theme_toggle.setStyleSheet(self.button_style())
        self.theme_toggle.clicked.connect(self.toggle_theme)
        self.layout.addWidget(self.theme_toggle)

        # Initialize in dark mode
        self.set_dark_mode()

    def perform_search(self):
        """Perform the search based on the query from the search bar."""
        query = self.search_bar.text().strip()
        if not query:
            self.output_area.setText("Please enter a topic to search.")
            return

        # Disable the search button and show loading message
        self.search_button.setEnabled(False)
        self.output_area.setText("Searching... Please wait...")

        # Perform the search based on the selected source
        if self.current_source == "Wikipedia":
            result, url = self.wikipedia_handler.fetch_wikipedia_info(query, self.summary_type)
            if not result:
                result = f"'{query}' not found in Wikipedia."
            self.source_reference_label.setText(f"Source: {url}" if url else "")  # Update the source reference
        elif self.current_source == "DialogPT":
            result = self.dialogpt_handler.generate_response(query)
            if not result or "error" in result.lower():
                result = f"Unable to generate response for '{query}'. Please try another topic."
            self.source_reference_label.setText("")  # Clear source reference for DialogPT

        # Re-enable the search button and display result
        self.search_button.setEnabled(True)
        self.output_area.setText(result)

    def toggle_theme(self):
        """Toggle between dark mode and light mode."""
        if self.is_dark_mode:
            self.set_light_mode()
            self.theme_toggle.setText("Switch to Dark Mode")
        else:
            self.set_dark_mode()
            self.theme_toggle.setText("Switch to Light Mode")
        self.is_dark_mode = not self.is_dark_mode

    def set_dark_mode(self):
        """Set dark mode theme."""
        self.setStyleSheet("background-color: #2c2c2c; color: white;")
        self.search_bar.setStyleSheet(self.search_bar_style())
        self.search_button.setStyleSheet(self.button_style())
        self.output_area.setStyleSheet(self.output_area_style())

    def set_light_mode(self):
        """Set light mode theme."""
        self.setStyleSheet("background-color: #f5f5f5; color: black;")
        self.search_bar.setStyleSheet(self.search_bar_style(light=True))
        self.search_button.setStyleSheet(self.button_style(light=True))
        self.output_area.setStyleSheet(self.output_area_style(light=True))

    def button_style(self, light=False):
        """Return the style for the buttons with hover effects."""
        if light:
            return (
                "QPushButton {"
                "background-color: #4caf50;"  # Light Green
                "color: white;"
                "border-radius: 10px;"
                "padding: 10px;"
                "}"
                "QPushButton:hover {"
                "background-color: #45a049;"
                "}"
            )
        else:
            return (
                "QPushButton {"
                "background-color: #0078d7;"  # Dark Blue
                "color: white;"
                "border-radius: 10px;"
                "padding: 10px;"
                "}"
                "QPushButton:hover {"
                "background-color: #0056a1;"
                "}"
            )

    def output_area_style(self, light=False):
        """Return the style for the output area."""
        if light:
            return "QTextEdit { background-color: white; color: black; }"
        return "QTextEdit { background-color: #3c3c3c; color: white; }"

    def search_bar_style(self, light=False):
        """Return the style for the search bar."""
        if light:
            return "QLineEdit { background-color: white; color: black; border: 2px solid #4caf50; border-radius: 5px; }"
        return "QLineEdit { background-color: #5c5c5c; color: white; border: 2px solid #0078d7; border-radius: 5px; }"

    def change_source(self, index):
        """Change the data source based on the selection."""
        self.current_source = self.source_selector.itemText(index)

    def set_summary_type(self, summary_type):
        """Set the summary type based on user selection."""
        self.summary_type = summary_type

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wiki_bot = WikiBotUI()
    wiki_bot.show()
    sys.exit(app.exec_())
