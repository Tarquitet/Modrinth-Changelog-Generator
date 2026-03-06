import os
import json
import platform
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QFileDialog, QRadioButton, 
                             QButtonGroup, QTextEdit, QMessageBox, QApplication, 
                             QGroupBox, QFrame, QTabWidget, QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPalette, QColor, QClipboard

from core.extractor import read_local_mrpack, fetch_modrinth_versions, download_specific_mrpack
from core.markdown_gen import generate_diff, generate_full_list

# --- HILOS DE TRABAJO ---

class VersionListWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, project_id):
        super().__init__()
        self.project_id = project_id

    def run(self):
        try:
            versions = fetch_modrinth_versions(self.project_id)
            self.finished.emit(versions)
        except Exception as e:
            self.error.emit(str(e))

class DownloadWorker(QThread):
    finished = pyqtSignal(dict, dict)
    error = pyqtSignal(str)

    def __init__(self, url, version_number):
        super().__init__()
        self.url = url
        self.version_number = version_number

    def run(self):
        try:
            metadata, mods = download_specific_mrpack(self.url, self.version_number)
            self.finished.emit(metadata, mods)
        except Exception as e:
            self.error.emit(str(e))

class LocalLoadWorker(QThread):
    finished = pyqtSignal(dict, dict)
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            metadata, mods = read_local_mrpack(self.path)
            self.finished.emit(metadata, mods)
        except Exception as e:
            self.error.emit(str(e))

# --- INTERFAZ PRINCIPAL ---

class ModpackTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modrinth Modpack Manager")
        self.resize(1000, 750)

        self.is_dark_mode = True

        self.old_mods = {}
        self.new_mods = {}
        self.old_metadata = {}
        self.new_metadata = {}
        
        self.old_info_state = 'default'
        self.new_info_state = 'default'
        self.save_status_state = 'default'
        
        self.available_versions = []
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_dir, "config.json")
        self.outputs_dir = os.path.join(base_dir, "outputs")

        self.init_ui()
        self.apply_theme()
        self.load_saved_session()

    def init_ui(self):
        main_layout = QHBoxLayout()

        # PANEL IZQUIERDO
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.btn_theme = QPushButton("Light Mode")
        self.btn_theme.clicked.connect(self.toggle_theme)
        left_panel.addWidget(self.btn_theme, alignment=Qt.AlignmentFlag.AlignRight)

        # 1. VERSION BASE
        group_base = QGroupBox("1. Base Version (Older)")
        layout_base = QVBoxLayout()
        
        self.tabs_base = QTabWidget()
        
        tab_modrinth = QWidget()
        layout_modrinth = QVBoxLayout()
        
        row_search = QHBoxLayout()
        self.input_modrinth_id = QLineEdit()
        self.input_modrinth_id.setPlaceholderText("Modrinth ID (e.g. buildtechcraft)")
        self.btn_search_versions = QPushButton("Search Versions")
        self.btn_search_versions.clicked.connect(self.action_search_versions)
        row_search.addWidget(self.input_modrinth_id)
        row_search.addWidget(self.btn_search_versions)
        
        row_select = QHBoxLayout()
        self.combo_versions = QComboBox()
        self.combo_versions.setEnabled(False)
        self.btn_download_version = QPushButton("Download Base")
        self.btn_download_version.setEnabled(False)
        self.btn_download_version.clicked.connect(self.action_download_base)
        row_select.addWidget(self.combo_versions)
        row_select.addWidget(self.btn_download_version)
        
        layout_modrinth.addLayout(row_search)
        layout_modrinth.addLayout(row_select)
        tab_modrinth.setLayout(layout_modrinth)
        
        tab_local_base = QWidget()
        layout_local_base = QVBoxLayout()
        self.btn_old_local = QPushButton("Select Local .mrpack (Base)")
        self.btn_old_local.clicked.connect(self.action_load_old_local)
        layout_local_base.addWidget(self.btn_old_local)
        tab_local_base.setLayout(layout_local_base)
        
        self.tabs_base.addTab(tab_modrinth, "From Modrinth")
        self.tabs_base.addTab(tab_local_base, "From Local File")
        
        layout_base.addWidget(self.tabs_base)
        
        self.lbl_old_info = QLabel("No base modpack loaded.")
        self.lbl_old_info.setWordWrap(True)
        layout_base.addWidget(self.lbl_old_info)
        
        group_base.setLayout(layout_base)
        left_panel.addWidget(group_base)

        # 2. VERSION NUEVA
        group_new = QGroupBox("2. Target Version (Newer - Local)")
        layout_new = QVBoxLayout()
        
        self.btn_new_local = QPushButton("Select Local .mrpack (Target)")
        self.btn_new_local.clicked.connect(self.action_load_new_local)
        layout_new.addWidget(self.btn_new_local)
        
        self.lbl_new_info = QLabel("No target modpack loaded.")
        self.lbl_new_info.setWordWrap(True)
        layout_new.addWidget(self.lbl_new_info)
        
        group_new.setLayout(layout_new)
        left_panel.addWidget(group_new)

        # 3. OPCIONES
        group_options = QGroupBox("3. Generation Options")
        layout_options = QVBoxLayout()
        
        self.radio_group = QButtonGroup(self)
        self.radio_diff = QRadioButton("Changelog (Diff)")
        self.radio_full = QRadioButton("Full Mod List")
        self.radio_diff.setChecked(True)
        self.radio_group.addButton(self.radio_diff)
        self.radio_group.addButton(self.radio_full)
        layout_options.addWidget(self.radio_diff)
        layout_options.addWidget(self.radio_full)

        btn_generate = QPushButton("Generate & Save Markdown")
        btn_generate.setStyleSheet("background-color: #2b78e4; color: white; font-weight: bold; padding: 12px; margin-top: 10px; border-radius: 4px;")
        btn_generate.clicked.connect(self.action_generate)
        layout_options.addWidget(btn_generate)
        
        group_options.setLayout(layout_options)
        left_panel.addWidget(group_options)

        # PANEL DERECHO
        right_panel = QVBoxLayout()
        
        self.lbl_save_status = QLabel("")
        self.lbl_save_status.setWordWrap(True)
        self.lbl_save_status.hide()
        right_panel.addWidget(self.lbl_save_status)

        lbl_output = QLabel("<b>Generated Markdown:</b>")
        right_panel.addWidget(lbl_output)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        right_panel.addWidget(self.output_text)

        # Controles de salida (Copiar, Borrar, Abrir Carpeta)
        row_actions = QHBoxLayout()
        
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self.action_copy_clipboard)
        
        self.btn_clear = QPushButton("Clear Output")
        self.btn_clear.clicked.connect(self.action_clear_output)
        
        self.btn_open_folder = QPushButton("Open Outputs Folder")
        self.btn_open_folder.clicked.connect(self.action_open_folder)

        row_actions.addWidget(self.btn_copy)
        row_actions.addWidget(self.btn_clear)
        row_actions.addWidget(self.btn_open_folder)
        
        right_panel.addLayout(row_actions)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setFixedWidth(400)

        main_layout.addWidget(left_widget)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        main_layout.addWidget(right_widget)

        self.setLayout(main_layout)

    # --- ACCIONES DE SALIDA (NUEVO) ---

    def action_copy_clipboard(self):
        text = self.output_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.lbl_save_status.setText("<b>Copied to clipboard!</b>")
            self.save_status_state = 'default'
            self.lbl_save_status.setStyleSheet(self.get_label_style(self.save_status_state))
            self.lbl_save_status.show()

    def action_clear_output(self):
        self.output_text.clear()
        self.lbl_save_status.hide()

    def action_open_folder(self):
        os.makedirs(self.outputs_dir, exist_ok=True)
        if platform.system() == "Windows":
            os.startfile(self.outputs_dir)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", self.outputs_dir])
        else:
            subprocess.Popen(["xdg-open", self.outputs_dir])

    # --- LOGICA DE SESION ---

    def save_setting(self, key, value):
        config = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except: pass
        config[key] = value
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except: pass

    def load_saved_session(self):
        if not os.path.exists(self.config_path):
            return
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            if "modrinth_id" in config:
                self.input_modrinth_id.setText(config["modrinth_id"])
            if config.get("target_path") and os.path.exists(config["target_path"]):
                self.execute_load_new_local(config["target_path"])
        except: pass

    # --- TEMAS ---

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        app = QApplication.instance()
        palette = QPalette()

        if self.is_dark_mode:
            self.btn_theme.setText("Light Mode")
            palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        else:
            self.btn_theme.setText("Dark Mode")
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(225, 225, 225))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

        app.setPalette(palette)
        self.update_dynamic_styles()

    def update_dynamic_styles(self):
        if self.is_dark_mode:
            self.output_text.setStyleSheet("font-family: Consolas, monospace; background-color: #1e1e1e; color: #d4d4d4; padding: 10px; border: 1px solid #555;")
        else:
            self.output_text.setStyleSheet("font-family: Consolas, monospace; background-color: #ffffff; color: #333333; padding: 10px; border: 1px solid #ccc;")

        self.lbl_old_info.setStyleSheet(self.get_label_style(self.old_info_state))
        self.lbl_new_info.setStyleSheet(self.get_label_style(self.new_info_state))
        
        if not self.lbl_save_status.isHidden():
            self.lbl_save_status.setStyleSheet(self.get_label_style(self.save_status_state))

    def get_label_style(self, state):
        if state == 'success':
            if self.is_dark_mode: return "background-color: #153a21; color: #85e0a3; padding: 10px; border-radius: 5px; border: 1px solid #1e5230;"
            return "background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb;"
        elif state == 'error':
            if self.is_dark_mode: return "background-color: #4a151b; color: #ffb3b8; padding: 10px; border-radius: 5px; border: 1px solid #6b1e26;"
            return "background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; border: 1px solid #f5c6cb;"
        else:
            if self.is_dark_mode: return "background-color: #2b2b2b; color: #ffffff; padding: 10px; border-radius: 5px; border: 1px solid #444;"
            return "background-color: #e9ecef; color: #000000; padding: 10px; border-radius: 5px; border: 1px solid #ced4da;"

    # --- LOGICA DE EXTRACCION ---

    def format_metadata_text(self, metadata, mod_count):
        return f"<b>Name:</b> {metadata.get('name', 'Unknown')}<br><b>Version:</b> {metadata.get('version', 'Unknown')}<br><b>Minecraft:</b> {metadata.get('minecraft', 'Unknown')}<br><b>Total Mods:</b> {mod_count}"

    def action_search_versions(self):
        project_id = self.input_modrinth_id.text().strip()
        if not project_id:
            QMessageBox.warning(self, "Error", "Please enter a Modrinth ID.")
            return

        self.save_setting("modrinth_id", project_id)
        
        self.btn_search_versions.setEnabled(False)
        self.combo_versions.clear()
        self.combo_versions.addItem("Searching...")
        self.combo_versions.setEnabled(False)
        self.btn_download_version.setEnabled(False)

        self.worker_search = VersionListWorker(project_id)
        self.worker_search.finished.connect(self.on_versions_found)
        self.worker_search.error.connect(self.on_versions_error)
        self.worker_search.start()

    def on_versions_found(self, versions):
        self.available_versions = versions
        self.combo_versions.clear()
        for v in versions:
            self.combo_versions.addItem(f"{v['version_number']} - {v['name']}")
            
        self.combo_versions.setEnabled(True)
        self.btn_download_version.setEnabled(True)
        self.btn_search_versions.setEnabled(True)

    def on_versions_error(self, error_msg):
        self.combo_versions.clear()
        self.combo_versions.addItem("Error finding versions.")
        self.btn_search_versions.setEnabled(True)
        QMessageBox.critical(self, "Error API", error_msg)

    def action_download_base(self):
        idx = self.combo_versions.currentIndex()
        if idx < 0: return
        
        selected = self.available_versions[idx]
        
        self.lbl_old_info.setText("<i>Downloading selected version...</i>")
        self.old_info_state = 'default'
        self.update_dynamic_styles()
        self.btn_download_version.setEnabled(False)

        self.worker_download = DownloadWorker(selected['url'], selected['version_number'])
        self.worker_download.finished.connect(self.on_old_loaded)
        self.worker_download.error.connect(self.on_old_error)
        self.worker_download.start()

    def action_load_old_local(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select base .mrpack", "", "Modrinth Pack (*.mrpack)")
        if path:
            self.lbl_old_info.setText("<i>Reading local file...</i>")
            self.old_info_state = 'default'
            self.update_dynamic_styles()
            
            self.worker_base = LocalLoadWorker(path)
            self.worker_base.finished.connect(self.on_old_loaded)
            self.worker_base.error.connect(self.on_old_error)
            self.worker_base.start()

    def on_old_loaded(self, metadata, mods):
        self.old_metadata = metadata
        self.old_mods = mods
        self.lbl_old_info.setText(self.format_metadata_text(metadata, len(mods)))
        self.old_info_state = 'success'
        self.update_dynamic_styles()
        self.btn_download_version.setEnabled(True)

    def on_old_error(self, error_msg):
        self.lbl_old_info.setText(f"<b>Error:</b> {error_msg}")
        self.old_info_state = 'error'
        self.update_dynamic_styles()
        self.btn_download_version.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)

    def action_load_new_local(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select target .mrpack", "", "Modrinth Pack (*.mrpack)")
        if path:
            self.execute_load_new_local(path)

    def execute_load_new_local(self, path):
        self.save_setting("target_path", path)
        
        self.lbl_new_info.setText("<i>Reading local file...</i>")
        self.new_info_state = 'default'
        self.update_dynamic_styles()
        
        self.worker_target = LocalLoadWorker(path)
        self.worker_target.finished.connect(self.on_new_loaded)
        self.worker_target.error.connect(self.on_new_error)
        self.worker_target.start()

    def on_new_loaded(self, metadata, mods):
        self.new_metadata = metadata
        self.new_mods = mods
        self.lbl_new_info.setText(self.format_metadata_text(metadata, len(mods)))
        self.new_info_state = 'success'
        self.update_dynamic_styles()

    def on_new_error(self, error_msg):
        self.lbl_new_info.setText(f"<b>Error:</b> {error_msg}")
        self.new_info_state = 'error'
        self.update_dynamic_styles()
        QMessageBox.critical(self, "Error", error_msg)

    def action_generate(self):
        if not self.new_mods:
            QMessageBox.warning(self, "Warning", "Load a target .mrpack first.")
            return

        if self.radio_diff.isChecked():
            if not self.old_mods:
                QMessageBox.warning(self, "Warning", "Base version is required to generate a changelog.")
                return
                
            if self.old_metadata.get('version') == self.new_metadata.get('version'):
                reply = QMessageBox.question(self, "Same Version Detected", 
                                             "It seems you are comparing the exact same version. The changelog might be empty. Do you want to continue?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

            result = generate_diff(self.old_mods, self.new_mods)
            prefix = "changelog"
        else:
            result = generate_full_list(self.new_mods)
            prefix = "modlist"

        project_name = self.new_metadata.get('name', 'Unknown_Project').replace(" ", "_")
        version_name = self.new_metadata.get('version', 'unknown').replace(" ", "_")
        
        output_dir = os.path.join(self.outputs_dir, project_name)
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{prefix}_{version_name}.md"
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(result)
            self.save_status_state = 'success'
            self.lbl_save_status.setText(f"<b>SUCCESS:</b> File saved to:<br><i>{filepath}</i>")
        except Exception as e:
            self.save_status_state = 'error'
            self.lbl_save_status.setText(f"<b>ERROR SAVING FILE:</b><br>{e}")

        self.lbl_save_status.setStyleSheet(self.get_label_style(self.save_status_state))
        self.lbl_save_status.show()
        self.output_text.setPlainText(result)