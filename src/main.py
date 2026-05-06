#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QPushButton, QSpinBox, 
                             QLabel, QMessageBox, QListWidgetItem, QLineEdit,
                             QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from logic import (get_installed_apps, generate_startup_script, save_config, 
                   load_config, enable_autostart, uninstall_everything)

class StartupManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Inicialização Profissional")
        self.setMinimumSize(900, 650)
        
        # Carregar apps do sistema
        self.all_apps = get_installed_apps()
        
        self.init_ui()
        self.load_saved_data()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- ESTILO GERAL ---
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; color: #cdd6f4; }
            QLabel { color: #cdd6f4; font-weight: bold; }
            QListWidget { background-color: #313244; border-radius: 8px; padding: 5px; color: #cdd6f4; }
            QLineEdit { background-color: #313244; border: 1px solid #45475a; border-radius: 5px; padding: 8px; color: white; }
            QPushButton { border-radius: 5px; padding: 8px; font-weight: bold; }
            QSpinBox { background-color: #313244; color: white; padding: 5px; }
        """)

        # --- COLUNA ESQUERDA: Busca e Apps ---
        left_column = QVBoxLayout()
        
        left_column.addWidget(QLabel("🔍 PESQUISAR APLICATIVOS"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ex: Motrix, JamesDSP...")
        self.search_input.textChanged.connect(self.filter_apps)
        left_column.addWidget(self.search_input)
        
        self.app_list_widget = QListWidget()
        self.populate_app_list()
        left_column.addWidget(self.app_list_widget)
        
        self.add_btn = QPushButton("ADICIONAR À FILA ➔")
        self.add_btn.setStyleSheet("background-color: #89b4fa; color: #11111b;")
        self.add_btn.clicked.connect(self.add_app_to_queue)
        left_column.addWidget(self.add_btn)

        # --- COLUNA DIREITA: Fila e Configurações ---
        right_column = QVBoxLayout()
        
        right_column.addWidget(QLabel("📋 FILA DE INICIALIZAÇÃO (ORDEM REAL)"))
        self.queue_list_widget = QListWidget()
        right_column.addWidget(self.queue_list_widget)

        # Botões de Reordenação
        order_box = QHBoxLayout()
        self.btn_up = QPushButton("⬆ SUBIR")
        self.btn_up.setStyleSheet("background-color: #45475a; color: white;")
        self.btn_up.clicked.connect(lambda: self.move_item(-1))
        
        self.btn_down = QPushButton("⬇ DESCER")
        self.btn_down.setStyleSheet("background-color: #45475a; color: white;")
        self.btn_down.clicked.connect(lambda: self.move_item(1))
        
        order_box.addWidget(self.btn_up)
        order_box.addWidget(self.btn_down)
        right_column.addLayout(order_box)

        # Configurações de Delay
        settings_frame = QFrame()
        settings_frame.setStyleSheet("background-color: #45475a; border-radius: 10px;")
        settings_layout = QVBoxLayout(settings_frame)
        
        delay_row = QHBoxLayout()
        delay_row.addWidget(QLabel("ATRASO PARA ESTE APP (S):"))
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 600)
        self.delay_spin.setValue(5)
        delay_row.addWidget(self.delay_spin)
        settings_layout.addLayout(delay_row)
        
        self.remove_btn = QPushButton("REMOVER DA FILA")
        self.remove_btn.setStyleSheet("background-color: #f38ba8; color: #11111b;")
        self.remove_btn.clicked.connect(self.remove_from_queue)
        settings_layout.addWidget(self.remove_btn)
        
        right_column.addWidget(settings_frame)

        # Ações Finais
        self.save_btn = QPushButton("✅ APLICAR E ATIVAR NO SISTEMA")
        self.save_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-size: 14px; padding: 15px;")
        self.save_btn.clicked.connect(self.save_everything)
        right_column.addWidget(self.save_btn)

        self.reset_btn = QPushButton("🗑️ LIMPAR TUDO (DESINSTALAR)")
        self.reset_btn.setStyleSheet("color: #f38ba8; background: transparent; border: 1px solid #f38ba8;")
        self.reset_btn.clicked.connect(self.full_reset)
        right_column.addWidget(self.reset_btn)

        # Unir Colunas
        main_layout.addLayout(left_column, 4)
        main_layout.addLayout(right_column, 5)

    def populate_app_list(self, filter_text=""):
        self.app_list_widget.clear()
        colors = {"Sistema (RPM)": "#a6e3a1", "Flatpak": "#89b4fa", "Usuário/AppImage": "#fab387"}
        
        for app in self.all_apps:
            if filter_text.lower() in app['name'].lower():
                item = QListWidgetItem(f"[{app['category']}] {app['name']}")
                item.setForeground(QColor(colors.get(app['category'], "white")))
                item.setData(Qt.ItemDataRole.UserRole, app)
                self.app_list_widget.addItem(item)

    def filter_apps(self):
        self.populate_app_list(self.search_input.text())

    def add_app_to_queue(self, app_data=None, delay=None):
        if not app_data:
            selected = self.app_list_widget.currentItem()
            if not selected: return
            app_data = selected.data(Qt.ItemDataRole.UserRole)
            delay = self.delay_spin.value()

        item_text = f"{app_data['name']} (Espera {delay}s)"
        list_item = QListWidgetItem(item_text)
        list_item.setData(Qt.ItemDataRole.UserRole, {
            "name": app_data['name'], 
            "exec": app_data['exec'], 
            "delay": delay
        })
        self.queue_list_widget.addItem(list_item)

    def load_saved_data(self):
        data = load_config()
        for app in data:
            self.add_app_to_queue(app_data={"name": app['name'], "exec": app['exec']}, delay=app['delay'])

    def move_item(self, direction):
        row = self.queue_list_widget.currentRow()
        if row < 0: return
        target = row + direction
        if 0 <= target < self.queue_list_widget.count():
            item = self.queue_list_widget.takeItem(row)
            self.queue_list_widget.insertItem(target, item)
            self.queue_list_widget.setCurrentRow(target)

    def remove_from_queue(self):
        self.queue_list_widget.takeItem(self.queue_list_widget.currentRow())

    def save_everything(self):
        if self.queue_list_widget.count() == 0:
            QMessageBox.warning(self, "Fila Vazia", "Adicione apps antes de salvar.")
            return

        queue_data = []
        app_list_for_script = []
        
        for i in range(self.queue_list_widget.count()):
            data = self.queue_list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            queue_data.append(data)
            app_list_for_script.append((data['exec'], data['delay']))
        
        script_path = generate_startup_script(app_list_for_script)
        if script_path:
            save_config(queue_data)
            enable_autostart(script_path)
            QMessageBox.information(self, "Sucesso", "Configuração aplicada! Os apps iniciarão no próximo login.")

    def full_reset(self):
        reply = QMessageBox.question(self, "Confirmar Reset", 
                                   "Isso removerá o script, as configurações e o autostart. Deseja continuar?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            uninstall_everything()
            self.queue_list_widget.clear()
            QMessageBox.information(self, "Reset Concluído", "O sistema de inicialização foi removido.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("startup-manager")
    app.setDesktopFileName("startup-manager")
    app.setStyle("Fusion") # Estilo moderno e consistente
    window = StartupManagerApp()
    window.show()
    sys.exit(app.exec())