import sys
import os
from PyQt6.QtWidgets import QApplication
from brain import LumiBrain

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.gui.overlay import LumiOverlay

def main():
    app = QApplication(sys.argv)
    
    # Создаем мозг
    brain = LumiBrain()
    
    # Создаем оверлей и передаем ему мозг
    window = LumiOverlay(brain)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()