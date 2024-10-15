import sys
from PyQt5.QtWidgets import QApplication
from ui_modified import WikiBotUI  # Ensure this points to the updated UI

def main():
    app = QApplication(sys.argv)
    window = WikiBotUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
