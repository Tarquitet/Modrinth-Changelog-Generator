import sys
import subprocess

def install_dependencies():
    packages_to_install = []
    try:
        import requests
    except ImportError:
        packages_to_install.append("requests")
    try:
        import PyQt6
    except ImportError:
        packages_to_install.append("PyQt6")
        
    if packages_to_install:
        print(f"Instalando dependencias necesarias: {', '.join(packages_to_install)}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *packages_to_install])
            print("Instalación completada.")
        except subprocess.CalledProcessError as e:
            print(f"Error crítico al instalar: {e}")
            sys.exit(1)

install_dependencies()

from PyQt6.QtWidgets import QApplication
from ui.main_window import ModpackTool

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    tool = ModpackTool()
    tool.show()
    sys.exit(app.exec())