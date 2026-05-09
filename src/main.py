#!/usr/bin/env python3
import sys
import os
import locale
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
        
        # 1. Detector de Idioma Automático
        try:
            sys_lang = locale.getdefaultlocale()[0] # Ex: 'pt_BR' ou 'en_US'
            if sys_lang and sys_lang.startswith('pt'):
                self.lang = 'pt'
            else:
                self.lang = 'en'
        except:
            self.lang = 'en' # Fallback para inglês
        
        self.texts = {
            'pt': {
                'toggle': "Mudar para Inglês",
                'title': "Gerenciador de Inicialização Profissional",
                'search': "🔍 PESQUISAR APLICATIVOS",
                'queue': "📋 FILA DE INICIALIZAÇÃO (ORDEM REAL)",
                'add': "ADICIONAR À FILA ➔",
                'up': "⬆ SUBIR",
                'down': "⬇ DESCER",
                'delay': "ATRASO (S):",
                'args': "ARGUMENTOS ADICIONAIS:",
                'remove': "REMOVER DA FILA",
                'apply': "✅ APLICAR E ATIVAR NO SISTEMA",
                'reset': "🗑️ LIMPAR TUDO (DESINSTALAR)",
                'success': "Sucesso",
                'applied': "Configuração aplicada com argumentos!",
                'success': "Sucesso",
                'applied': "Configuração aplicada com argumentos!",
                'reset_title': "Confirmar Reset",
                'reset_msg': "Isso removerá o script, as configurações e o autostart. Deseja continuar?",
                'reset_done_title': "Reset Concluído",
                'reset_done_msg': "O sistema de inicialização foi removido.",
                'empty_title': "Fila Vazia",
                'empty_msg': "Adicione apps antes de salvar.",
                'args_placeholder': "Ex: --minimized, -startintray",
                'args_tip': "Comandos extras para o programa (consulte o manual do app)",
                'search_placeholder': "Ex: Motrix, JamesDSP..."
            },
            'en': {
                'toggle': "Switch to Portuguese",
                'title': "Professional Startup Manager",
                'search': "🔍 SEARCH APPLICATIONS",
                'queue': "📋 STARTUP QUEUE (REAL ORDER)",
                'add': "ADD TO QUEUE ➔",
                'up': "⬆ MOVE UP",
                'down': "⬇ MOVE DOWN",
                'delay': "DELAY (S):",
                'args': "ADDITIONAL ARGUMENTS:",
                'remove': "REMOVE FROM QUEUE",
                'apply': "✅ APPLY AND ENABLE ON SYSTEM",
                'reset': "🗑️ CLEAR EVERYTHING (UNINSTALL)",
                'success': "Success",
                'applied': "Configuration applied with arguments!",
                'success': "Success",
                'applied': "Configuration applied with arguments!",
                'reset_title': "Confirm Reset",
                'reset_msg': "This will remove the script, settings, and autostart. Do you want to continue?",
                'reset_done_title': "Reset Finished",
                'reset_done_msg': "The startup system has been removed.",
                'empty_title': "Empty Queue",
                'empty_msg': "Add apps before saving.",
                'args_placeholder': "Ex: --minimized, -startintray",
                'args_tip': "Extra commands for the program (check the app's manual)",
                'search_placeholder': "Ex: Motrix, JamesDSP..."
            }
        }
        
        self.setWindowTitle(self.texts[self.lang]['title'])
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

        # Botão de Troca de Idioma
        self.lang_btn = QPushButton(self.texts[self.lang]['toggle'])
        self.lang_btn.setStyleSheet("background-color: #585b70; color: white; font-size: 10px;")
        self.lang_btn.clicked.connect(self.toggle_language)
        left_column.addWidget(self.lang_btn)
        
        self.label_search = QLabel(self.texts[self.lang]['search'])
        left_column.addWidget(self.label_search)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ex: Motrix, JamesDSP...")
        self.search_input.textChanged.connect(self.filter_apps)
        left_column.addWidget(self.search_input)
        
        self.app_list_widget = QListWidget()
        self.populate_app_list()
        left_column.addWidget(self.app_list_widget)
        
        self.add_btn = QPushButton(self.texts[self.lang]['add'])
        self.add_btn.setStyleSheet("background-color: #89b4fa; color: #11111b;")
        self.add_btn.clicked.connect(self.add_app_to_queue)
        left_column.addWidget(self.add_btn)

        # --- COLUNA DIREITA: Fila e Configurações ---
        right_column = QVBoxLayout()
        
        self.label_queue = QLabel(self.texts[self.lang]['queue'])
        right_column.addWidget(self.label_queue)
        self.queue_list_widget = QListWidget()
        right_column.addWidget(self.queue_list_widget)

        # Botões de Reordenação
        order_box = QHBoxLayout()
        self.btn_up = QPushButton(self.texts[self.lang]['up'])
        self.btn_up.setStyleSheet("background-color: #45475a; color: white;")
        self.btn_up.clicked.connect(lambda: self.move_item(-1))
        
        self.btn_down = QPushButton(self.texts[self.lang]['down'])
        self.btn_down.setStyleSheet("background-color: #45475a; color: white;")
        self.btn_down.clicked.connect(lambda: self.move_item(1))
        
        order_box.addWidget(self.btn_up)
        order_box.addWidget(self.btn_down)
        right_column.addLayout(order_box)

        # Configurações de Delay e Argumentos
        settings_frame = QFrame()
        settings_frame.setStyleSheet("background-color: #45475a; border-radius: 10px;")
        settings_layout = QVBoxLayout(settings_frame)
        
        # Linha do Delay
        delay_row = QHBoxLayout()
        self.label_delay = QLabel(self.texts[self.lang]['delay'])
        delay_row.addWidget(self.label_delay)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 600)
        self.delay_spin.setValue(5)
        delay_row.addWidget(self.delay_spin)
        settings_layout.addLayout(delay_row)

        # NOVA LINHA: Argumentos
        args_row = QVBoxLayout()
        self.label_args = QLabel(self.texts[self.lang]['args'])
        args_row.addWidget(self.label_args)
        self.args_input = QLineEdit()
        self.args_input.setPlaceholderText(self.texts[self.lang]['args_placeholder'])
        self.args_input.setToolTip(self.texts[self.lang]['args_tip'])
        args_row.addWidget(self.args_input)
        settings_layout.addLayout(args_row)
        
        self.remove_btn = QPushButton(self.texts[self.lang]['remove'])
        self.remove_btn.setStyleSheet("background-color: #f38ba8; color: #11111b;")
        self.remove_btn.clicked.connect(self.remove_from_queue)
        settings_layout.addWidget(self.remove_btn)
        
        right_column.addWidget(settings_frame)

        # Ações Finais
        self.save_btn = QPushButton(self.texts[self.lang]['apply'])
        self.save_btn.setStyleSheet("background-color: #a6e3a1; color: #11111b; font-size: 14px; padding: 15px;")
        self.save_btn.clicked.connect(self.save_everything)
        right_column.addWidget(self.save_btn)

        self.reset_btn = QPushButton(self.texts[self.lang]['reset'])
        self.reset_btn.setStyleSheet("color: #f38ba8; background: transparent; border: 1px solid #f38ba8;")
        self.reset_btn.clicked.connect(self.full_reset)
        right_column.addWidget(self.reset_btn)

        # Unir Colunas
        main_layout.addLayout(left_column, 4)
        main_layout.addLayout(right_column, 5)

    def toggle_language(self):
        # Inverte o idioma
        self.lang = 'en' if self.lang == 'pt' else 'pt'

        # Atualiza os placeholders e tooltips usando as chaves corretas
        self.search_input.setPlaceholderText(self.texts[self.lang]['search_placeholder'])
        self.args_input.setPlaceholderText(self.texts[self.lang]['args_placeholder']) # Use a chave do dicionário
        self.args_input.setToolTip(self.texts[self.lang]['args_tip'])
        
        # Atualiza os textos da interface (Botões e Título)
        self.setWindowTitle(self.texts[self.lang]['title'])
        self.lang_btn.setText(self.texts[self.lang]['toggle'])
        self.add_btn.setText(self.texts[self.lang]['add'])
        self.save_btn.setText(self.texts[self.lang]['apply'])
        self.reset_btn.setText(self.texts[self.lang]['reset'])
        self.remove_btn.setText(self.texts[self.lang]['remove'])
        self.btn_up.setText(self.texts[self.lang]['up'])
        self.btn_down.setText(self.texts[self.lang]['down'])
        
        # NOVAS LINHAS: Atualiza os Labels fixos
        self.label_search.setText(self.texts[self.lang]['search'])
        self.label_queue.setText(self.texts[self.lang]['queue'])
        self.label_delay.setText(self.texts[self.lang]['delay'])
        self.label_args.setText(self.texts[self.lang]['args'])
        
        # Atualiza o Placeholder da busca
        search_placeholder = "Ex: Motrix, JamesDSP..." if self.lang == 'pt' else "Ex: Motrix, JamesDSP..."
        self.search_input.setPlaceholderText(search_placeholder)

        QMessageBox.information(self, 
                                "Language Changed" if self.lang == 'en' else "Idioma Alterado", 
                                "Language changed to English" if self.lang == 'en' else "Idioma alterado para Português")    

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

    def add_app_to_queue(self, app_data=None, delay=None, args=None):
        if not app_data:
            selected = self.app_list_widget.currentItem()
            if not selected: return
            app_data = selected.data(Qt.ItemDataRole.UserRole)
            delay = self.delay_spin.value()
            args = self.args_input.text().strip() # Captura os argumentos digitados

        # Se args for None (carregamento de arquivo antigo), vira string vazia
        args = args if args else ""
        
        display_text = f"{app_data['name']} (Espera {delay}s)"
        if args:
            display_text += f" [Args: {args}]"

        list_item = QListWidgetItem(display_text)
        list_item.setData(Qt.ItemDataRole.UserRole, {
            "name": app_data['name'], 
            "exec": app_data['exec'], 
            "delay": delay,
            "args": args # Salva os argumentos no item da lista
        })
        self.queue_list_widget.addItem(list_item)
        self.args_input.clear() # Limpa o campo para o próximo app

    def load_saved_data(self):
        data = load_config()
        for app in data:
            self.add_app_to_queue(
                app_data={"name": app['name'], "exec": app['exec']}, 
                delay=app['delay'],
                args=app.get('args', "") # Usa .get para evitar erro se a chave não existir
            )

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
            QMessageBox.warning(self, self.texts[self.lang]['empty_title'], self.texts[self.lang]['empty_msg'])
            return

        queue_data = []
        app_list_for_script = []
        
        for i in range(self.queue_list_widget.count()):
            data = self.queue_list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            queue_data.append(data)
            app_list_for_script.append((data['exec'], data['delay'], data.get('args', "")))
        
        script_path = generate_startup_script(app_list_for_script)
        if script_path:
            save_config(queue_data)
            enable_autostart(script_path)
            QMessageBox.information(self, self.texts[self.lang]['success'], self.texts[self.lang]['applied'])

    def full_reset(self):
        reply = QMessageBox.question(self, 
                                   self.texts[self.lang]['reset_title'], 
                                   self.texts[self.lang]['reset_msg'],
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            uninstall_everything()
            self.queue_list_widget.clear()
            QMessageBox.information(self, 
                                   self.texts[self.lang]['reset_done_title'], 
                                   self.texts[self.lang]['reset_done_msg'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("startup-manager")
    app.setDesktopFileName("startup-manager")
    app.setStyle("Fusion") # Estilo moderno e consistente
    window = StartupManagerApp()
    window.show()
    sys.exit(app.exec())