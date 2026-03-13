import sys
import os
from PyQt6.QtWidgets import QApplication
from brain import LumiBrain
from lumi_books import LumiBooks

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.gui.overlay import LumiOverlay

def main():
    app = QApplication(sys.argv)
    
    # Создаем мозг
    brain = LumiBrain()
    lumi_books = LumiBooks()
    
    # Создаем оверлей и передаем ему мозг
    window = LumiOverlay(brain, lumi_books)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()