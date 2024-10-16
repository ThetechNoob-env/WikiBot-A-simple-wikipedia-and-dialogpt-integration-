from PyQt5.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QApplication,
    QMessageBox,
    QTabWidget,
    QGridLayout,
    QProgressBar,
    QListWidget,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
import os
import sys
import json
from wiki_modified import WikipediaHandler  # Import WikipediaHandler from wiki_modified
from dialogpt import DialogPTHandler

# Resource path function
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

class SearchThread(QThread):
    """Thread for performing searches without freezing the UI."""
    result_ready = pyqtSignal(str, str, str)  # result, source, url
    progress_update = pyqtSignal(int)  # For progress updates

    def __init__(self, query, source, summary_type, wikipedia_handler, dialogpt_handler):
        super().__init__()
        self.query = query
        self.source = source
        self.summary_type = summary_type
        self.wikipedia_handler = wikipedia_handler
        self.dialogpt_handler = dialogpt_handler

    def run(self):
        """Run the search and emit the results."""
        self.progress_update.emit(25)  # Simulate starting progress
        if self.source == "Wikipedia":
            result, url = self.wikipedia_handler.fetch_wikipedia_info(self.query, self.summary_type)
            self.progress_update.emit(75)  # Simulate progress update during fetching
            if not result:
                result = f"'{self.query}' not found in Wikipedia."
            self.result_ready.emit(result, "Wikipedia Response", url)
        elif self.source == "DialogPT":
            result = self.dialogpt_handler.generate_response(self.query)
            self.progress_update.emit(75)  # Simulate progress update during fetching
            if not result or "error" in result.lower():
                result = f"Unable to generate response for '{self.query}'. Please try another topic."
            self.result_ready.emit(result, "DialogPT Response", "")

        self.progress_update.emit(100)  # Simulate finishing progress

class WikiBotUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize Wikipedia and DialogPT handlers
        self.wikipedia_handler = WikipediaHandler()  # WikipediaHandler instance
        self.dialogpt_handler = DialogPTHandler()
        self.current_source = "Wikipedia"  # Default to Wikipedia
        self.is_dark_mode = True  # Start with dark mode by default
        self.summary_type = "Medium"  # Set default summary type
        self.history = self.load_search_history()
        self.cache = {}  # Cache to store fetched results

        self.initUI()

    def initUI(self):
        """Set up the main UI components."""
        self.setWindowTitle("🌍 WikiBot - Your AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(self.dark_style())  # Set to dark style initially

        # Set up the central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        # Sidebar for navigation
        self.sidebar_layout = QVBoxLayout()
        self.layout.addLayout(self.sidebar_layout, 0, 0, 1, 1)

        # Title label
        self.title_label = QLabel("🌐 WikiBot AI Assistant", self)
        self.title_label.setFont(QFont("Helvetica Neue", 32, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.title_label)

        # Search bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("🔍 Enter a topic to search...")
        self.search_bar.setFont(QFont("Helvetica Neue", 18))
        self.search_bar.textChanged.connect(self.update_suggestions)  # Connect text change to suggestion method
        self.sidebar_layout.addWidget(self.search_bar)

        # Suggestions list
        self.suggestions_list = QListWidget(self)
        self.suggestions_list.setVisible(False)
        self.suggestions_list.itemClicked.connect(self.fill_suggestion)  # Fill suggestion on click
        self.sidebar_layout.addWidget(self.suggestions_list)

        # Source selector
        self.source_selector = QComboBox(self)
        self.source_selector.setFont(QFont("Helvetica Neue", 18))
        self.source_selector.addItem("Wikipedia")
        self.source_selector.addItem("DialogPT")
        self.source_selector.currentIndexChanged.connect(self.change_source)
        self.sidebar_layout.addWidget(self.source_selector)

        # Summary options dropdown
        self.summary_selector = QComboBox(self)
        self.summary_selector.setFont(QFont("Helvetica Neue", 18))
        self.summary_selector.addItem("Medium")
        self.summary_selector.addItem("Detailed")
        self.summary_selector.currentIndexChanged.connect(lambda index: self.set_summary_type(self.summary_selector.itemText(index)))
        self.sidebar_layout.addWidget(self.summary_selector)

        # Search button
        self.search_button = QPushButton("🔍 Search", self)
        self.search_button.setFont(QFont("Helvetica Neue", 20))
        self.search_button.clicked.connect(self.perform_search)
        self.sidebar_layout.addWidget(self.search_button)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.sidebar_layout.addWidget(self.progress_bar)

        # Output area with animations
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Helvetica Neue", 18))
        self.layout.addWidget(self.output_area, 0, 1, 1, 1)

        # Source reference label
        self.source_reference_label = QLabel("", self)
        self.source_reference_label.setFont(QFont("Helvetica Neue", 14))
        self.source_reference_label.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.source_reference_label, 1, 1)

        # Tabbed interface for additional features
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget, 2, 1)

        # Adding tabs
        self.create_tabs()

        # Dark Mode toggle button
        self.theme_toggle = QPushButton("🌙 Switch to Light Mode", self)
        self.theme_toggle.setFont(QFont("Helvetica Neue", 18))
        self.theme_toggle.clicked.connect(self.toggle_theme)
        self.sidebar_layout.addWidget(self.theme_toggle)

        # Reset Search History button
        self.reset_history_button = QPushButton("🗑️ Reset Search History", self)
        self.reset_history_button.setFont(QFont("Helvetica Neue", 18))
        self.reset_history_button.clicked.connect(self.reset_search_history)
        self.sidebar_layout.addWidget(self.reset_history_button)

        # About button
        self.about_button = QPushButton("ℹ️ About", self)
        self.about_button.setFont(QFont("Helvetica Neue", 18))
        self.about_button.clicked.connect(self.show_about)
        self.sidebar_layout.addWidget(self.about_button)

        # Initialize in dark mode
        self.set_dark_mode()

    def create_tabs(self):
        """Create additional tabs for extended functionality."""        
        tab1 = QWidget()
        tab2 = QWidget()
        self.tab_widget.addTab(tab1, "📜 Search History")
        self.tab_widget.addTab(tab2, "ℹ️ About")

        # Search History Tab Layout
        tab1_layout = QVBoxLayout()
        tab1.setLayout(tab1_layout)

        self.history_label = QLabel("📜 Search History", self)
        self.history_label.setFont(QFont("Helvetica Neue", 24, QFont.Weight.Bold))
        tab1_layout.addWidget(self.history_label)

        self.history_info = QTextEdit(self)
        self.history_info.setReadOnly(True)
        self.history_info.setFont(QFont("Helvetica Neue", 16))
        self.history_info.setPlainText("\n".join(self.history) if self.history else "No search history.")
        tab1_layout.addWidget(self.history_info)

        # About Tab Layout
        tab2_layout = QVBoxLayout()
        tab2.setLayout(tab2_layout)

        self.about_label = QLabel("About WikiBot", self)
        self.about_label.setFont(QFont("Helvetica Neue", 24, QFont.Weight.Bold))
        tab2_layout.addWidget(self.about_label)

        self.about_info = QTextEdit(self)
        self.about_info.setReadOnly(True)
        self.about_info.setFont(QFont("Helvetica Neue", 16))
        self.about_info.setPlainText("WikiBot is an AI-powered assistant to help you gather information from Wikipedia and DialogPT.")
        tab2_layout.addWidget(self.about_info)

    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.set_dark_mode() if self.is_dark_mode else self.set_light_mode()

    def set_dark_mode(self):
        """Set dark mode styles."""
        self.central_widget.setStyleSheet(self.dark_style())
        self.theme_toggle.setText("🌙 Switch to Light Mode")
        self.suggestions_list.setStyleSheet(self.suggestion_list_style())
        self.progress_bar.setStyleSheet(self.progress_bar_style())

    def set_light_mode(self):
        """Set light mode styles."""
        self.central_widget.setStyleSheet(self.light_style())
        self.theme_toggle.setText("🌙 Switch to Dark Mode")
        self.suggestions_list.setStyleSheet(self.suggestion_list_style())
        self.progress_bar.setStyleSheet(self.progress_bar_style())

    def dark_style(self):
        """Return dark style sheet."""
        return """
        QMainWindow {
            background-color: #121212;
        }
        QLabel {
            color: white;
        }
        QLineEdit, QTextEdit, QComboBox, QPushButton {
            background-color: #424242;
            color: white;
            border: 1px solid #9E9E9E;
        }
        QListWidget {
            background-color: #424242;
            color: white;
        }
        QProgressBar {
            background-color: #616161;
        }
        """

    def light_style(self):
        """Return light style sheet."""
        return """
        QMainWindow {
            background-color: white;
        }
        QLabel {
            color: black;
        }
        QLineEdit, QTextEdit, QComboBox, QPushButton {
            background-color: #E0E0E0;
            color: black;
            border: 1px solid #9E9E9E;
        }
        QListWidget {
            background-color: #E0E0E0;
            color: black;
        }
        QProgressBar {
            background-color: #BDBDBD;
        }
        """

    def suggestion_list_style(self):
        """Return style for the suggestion list."""
        return """
        QListWidget {
            background-color: #424242;
            color: white;
            border: 1px solid #9E9E9E;
        }
        """

    def progress_bar_style(self):
        """Return style for the progress bar."""
        return """
        QProgressBar {
            background-color: #616161;
            color: white;
        }
        """

    def change_source(self):
        """Change the current source based on the dropdown selection."""
        self.current_source = self.source_selector.currentText()

    def set_summary_type(self, summary_type):
        """Set the summary type based on the dropdown selection."""
        self.summary_type = summary_type

    def update_suggestions(self):
        """Update suggestions based on the current input in the search bar."""
        query = self.search_bar.text().strip()
        if query:
            suggestions = self.wikipedia_handler.auto_suggest(query)  # Changed here
            self.suggestions_list.clear()
            self.suggestions_list.addItems(suggestions)
            self.suggestions_list.setVisible(bool(suggestions))
        else:
            self.suggestions_list.clear()
            self.suggestions_list.setVisible(False)

    def fill_suggestion(self, item):
        """Fill the search bar with the selected suggestion."""
        self.search_bar.setText(item.text())
        self.suggestions_list.setVisible(False)

    def perform_search(self):
        """Initiate the search and display results."""
        query = self.search_bar.text().strip()
        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a search term.")
            return
        
        self.cache[query] = []  # Initialize cache for the query
        self.progress_bar.setVisible(True)  # Show progress bar
        self.progress_bar.setValue(0)  # Reset progress bar
        
        # Start the search thread
        self.search_thread = SearchThread(query, self.current_source, self.summary_type, self.wikipedia_handler, self.dialogpt_handler)
        self.search_thread.result_ready.connect(self.display_results)
        self.search_thread.progress_update.connect(self.update_progress)
        self.search_thread.start()

        # Save search history
        self.history.append(query)
        self.save_search_history()

    def update_progress(self, value):
        """Update the progress bar value."""
        self.progress_bar.setValue(value)

    def display_results(self, result, source, url):
        """Display the search results in the output area."""
        self.output_area.setPlainText(result)
        self.source_reference_label.setText(f"Source: {source} | URL: {url if url else 'N/A'}")
        self.progress_bar.setVisible(False)  # Hide progress bar after operation

    def load_search_history(self):
        """Load the search history from a JSON file."""
        try:
            with open('search_history.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_search_history(self):
        """Save the search history to a JSON file."""
        with open('search_history.json', 'w') as file:
            json.dump(self.history, file)

    def reset_search_history(self):
        """Reset the search history."""
        self.history = []
        self.save_search_history()
        self.history_info.setPlainText("No search history.")

    def show_about(self):
        """Show information about the application."""
        QMessageBox.information(self, "About WikiBot", "WikiBot is an AI-powered assistant to help you gather information from Wikipedia and DialogPT.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WikiBotUI()
    window.show()
    sys.exit(app.exec_())
