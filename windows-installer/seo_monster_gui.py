#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO Monster - Windows GUI Application
Графический интерфейс для управления SEO Monster на Windows
"""

import os
import sys
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from pathlib import Path
import socket
import time

# Константы
APP_NAME = "SEO Monster"
APP_VERSION = "2.0.0"
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_PORT = 5200

class SEOMonsterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Определяем базовую директорию
        self.base_dir = self.find_project_dir()
        
        # Процессы
        self.backend_process = None
        self.frontend_process = None
        
        # Статусы
        self.backend_running = False
        self.frontend_running = False
        
        # Настройки темы
        self.dark_mode = True
        self.setup_theme()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Проверяем статус при запуске
        self.check_status()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def find_project_dir(self):
        """Находит директорию проекта"""
        # Пробуем найти относительно исполняемого файла
        if getattr(sys, 'frozen', False):
            # Если запущено как exe
            exe_dir = Path(sys.executable).parent
        else:
            # Если запущено как скрипт
            exe_dir = Path(__file__).parent
        
        # Проверяем возможные расположения
        possible_paths = [
            exe_dir.parent,  # windows-installer -> seo-monster
            exe_dir,
            Path.cwd(),
            Path.home() / "seo-monster-app",
            Path.home() / "seo-monster",
        ]
        
        for path in possible_paths:
            if (path / "backend" / "main.py").exists():
                return path
        
        return exe_dir.parent
    
    def setup_theme(self):
        """Настройка темы приложения"""
        self.style = ttk.Style()
        
        if self.dark_mode:
            self.bg_color = "#1a1a2e"
            self.fg_color = "#eaeaea"
            self.accent_color = "#4a90d9"
            self.success_color = "#4caf50"
            self.error_color = "#f44336"
            self.warning_color = "#ff9800"
            self.card_bg = "#16213e"
            self.button_bg = "#0f3460"
        else:
            self.bg_color = "#f5f5f5"
            self.fg_color = "#333333"
            self.accent_color = "#2196f3"
            self.success_color = "#4caf50"
            self.error_color = "#f44336"
            self.warning_color = "#ff9800"
            self.card_bg = "#ffffff"
            self.button_bg = "#e0e0e0"
        
        self.root.configure(bg=self.bg_color)
        
        # Настройка стилей ttk
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.card_bg)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("Card.TLabel", background=self.card_bg, foreground=self.fg_color)
        self.style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), 
                           background=self.bg_color, foreground=self.fg_color)
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 12), 
                           background=self.bg_color, foreground=self.fg_color)
        self.style.configure("Status.TLabel", font=("Segoe UI", 10), 
                           background=self.card_bg, foreground=self.fg_color)
        
    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главный контейнер
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text=f"🦖 {APP_NAME}", style="Title.TLabel")
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(header_frame, text=f"v{APP_VERSION}", style="Subtitle.TLabel")
        version_label.pack(side=tk.LEFT, padx=(10, 0), pady=(10, 0))
        
        # Кнопка переключения темы
        self.theme_btn = tk.Button(header_frame, text="🌙" if self.dark_mode else "☀️",
                                   command=self.toggle_theme, font=("Segoe UI", 14),
                                   bg=self.button_bg, fg=self.fg_color, bd=0,
                                   activebackground=self.accent_color)
        self.theme_btn.pack(side=tk.RIGHT)
        
        # Карточки статуса
        status_frame = ttk.Frame(main_frame, style="TFrame")
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Backend статус
        self.backend_card = self.create_status_card(
            status_frame, "Backend (API)", "⚙️", "Остановлен", self.error_color
        )
        self.backend_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Frontend статус
        self.frontend_card = self.create_status_card(
            status_frame, "Frontend (UI)", "🖥️", "Остановлен", self.error_color
        )
        self.frontend_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame, style="Card.TFrame")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        control_frame.configure(padding=15)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(control_frame, style="Card.TFrame")
        buttons_frame.pack(fill=tk.X)
        
        self.start_all_btn = tk.Button(buttons_frame, text="▶️ Запустить всё",
                                       command=self.start_all, font=("Segoe UI", 11, "bold"),
                                       bg=self.success_color, fg="white", bd=0,
                                       activebackground="#388e3c", padx=20, pady=10)
        self.start_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_all_btn = tk.Button(buttons_frame, text="⏹️ Остановить всё",
                                      command=self.stop_all, font=("Segoe UI", 11, "bold"),
                                      bg=self.error_color, fg="white", bd=0,
                                      activebackground="#d32f2f", padx=20, pady=10)
        self.stop_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_browser_btn = tk.Button(buttons_frame, text="🌐 Открыть в браузере",
                                          command=self.open_browser, font=("Segoe UI", 11),
                                          bg=self.accent_color, fg="white", bd=0,
                                          activebackground="#1976d2", padx=20, pady=10)
        self.open_browser_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_btn = tk.Button(buttons_frame, text="🔄 Обновить статус",
                                     command=self.check_status, font=("Segoe UI", 11),
                                     bg=self.button_bg, fg=self.fg_color, bd=0,
                                     activebackground=self.accent_color, padx=20, pady=10)
        self.refresh_btn.pack(side=tk.RIGHT)
        
        # Отдельные кнопки для backend и frontend
        individual_frame = ttk.Frame(control_frame, style="Card.TFrame")
        individual_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.start_backend_btn = tk.Button(individual_frame, text="▶️ Backend",
                                           command=self.start_backend, font=("Segoe UI", 10),
                                           bg=self.button_bg, fg=self.fg_color, bd=0,
                                           padx=15, pady=8)
        self.start_backend_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_backend_btn = tk.Button(individual_frame, text="⏹️ Backend",
                                          command=self.stop_backend, font=("Segoe UI", 10),
                                          bg=self.button_bg, fg=self.fg_color, bd=0,
                                          padx=15, pady=8)
        self.stop_backend_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        self.start_frontend_btn = tk.Button(individual_frame, text="▶️ Frontend",
                                            command=self.start_frontend, font=("Segoe UI", 10),
                                            bg=self.button_bg, fg=self.fg_color, bd=0,
                                            padx=15, pady=8)
        self.start_frontend_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_frontend_btn = tk.Button(individual_frame, text="⏹️ Frontend",
                                           command=self.stop_frontend, font=("Segoe UI", 10),
                                           bg=self.button_bg, fg=self.fg_color, bd=0,
                                           padx=15, pady=8)
        self.stop_frontend_btn.pack(side=tk.LEFT)
        
        # Консоль логов
        log_frame = ttk.Frame(main_frame, style="Card.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True)
        log_frame.configure(padding=15)
        
        log_header = ttk.Frame(log_frame, style="Card.TFrame")
        log_header.pack(fill=tk.X, pady=(0, 10))
        
        log_title = ttk.Label(log_header, text="📋 Логи", font=("Segoe UI", 12, "bold"),
                             style="Card.TLabel")
        log_title.pack(side=tk.LEFT)
        
        clear_log_btn = tk.Button(log_header, text="🗑️ Очистить",
                                  command=self.clear_log, font=("Segoe UI", 9),
                                  bg=self.button_bg, fg=self.fg_color, bd=0,
                                  padx=10, pady=5)
        clear_log_btn.pack(side=tk.RIGHT)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, 
                                                   font=("Consolas", 10),
                                                   bg="#0d1117" if self.dark_mode else "#ffffff",
                                                   fg="#c9d1d9" if self.dark_mode else "#333333",
                                                   insertbackground=self.fg_color)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Информация
        info_frame = ttk.Frame(main_frame, style="TFrame")
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        info_text = f"📁 Директория проекта: {self.base_dir}"
        info_label = ttk.Label(info_frame, text=info_text, style="Subtitle.TLabel")
        info_label.pack(side=tk.LEFT)
        
        urls_label = ttk.Label(info_frame, 
                              text=f"🔗 Backend: http://localhost:{DEFAULT_BACKEND_PORT} | Frontend: http://localhost:{DEFAULT_FRONTEND_PORT}",
                              style="Subtitle.TLabel")
        urls_label.pack(side=tk.RIGHT)
        
    def create_status_card(self, parent, title, icon, status, color):
        """Создание карточки статуса"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.configure(padding=15)
        
        # Иконка и заголовок
        header = ttk.Frame(card, style="Card.TFrame")
        header.pack(fill=tk.X)
        
        icon_label = ttk.Label(header, text=icon, font=("Segoe UI", 20), style="Card.TLabel")
        icon_label.pack(side=tk.LEFT)
        
        title_label = ttk.Label(header, text=title, font=("Segoe UI", 12, "bold"), 
                               style="Card.TLabel")
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Статус
        status_frame = ttk.Frame(card, style="Card.TFrame")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        status_indicator = tk.Canvas(status_frame, width=12, height=12, 
                                    bg=self.card_bg, highlightthickness=0)
        status_indicator.create_oval(2, 2, 10, 10, fill=color, outline="")
        status_indicator.pack(side=tk.LEFT)
        
        status_label = ttk.Label(status_frame, text=status, style="Status.TLabel")
        status_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Сохраняем ссылки для обновления
        card.status_indicator = status_indicator
        card.status_label = status_label
        
        return card
    
    def update_status_card(self, card, status, color):
        """Обновление карточки статуса"""
        card.status_indicator.delete("all")
        card.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline="")
        card.status_label.configure(text=status)
        
    def toggle_theme(self):
        """Переключение темы"""
        self.dark_mode = not self.dark_mode
        self.setup_theme()
        # Перерисовываем интерфейс
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()
        self.check_status()
        
    def log(self, message, level="INFO"):
        """Добавление сообщения в лог"""
        timestamp = time.strftime("%H:%M:%S")
        colors = {
            "INFO": self.fg_color,
            "SUCCESS": self.success_color,
            "ERROR": self.error_color,
            "WARNING": self.warning_color
        }
        
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Очистка лога"""
        self.log_text.delete(1.0, tk.END)
        
    def is_port_in_use(self, port):
        """Проверка, занят ли порт"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
            
    def check_status(self):
        """Проверка статуса сервисов"""
        # Проверяем backend
        if self.is_port_in_use(DEFAULT_BACKEND_PORT):
            self.backend_running = True
            self.update_status_card(self.backend_card, "Работает", self.success_color)
        else:
            self.backend_running = False
            self.update_status_card(self.backend_card, "Остановлен", self.error_color)
            
        # Проверяем frontend
        if self.is_port_in_use(DEFAULT_FRONTEND_PORT):
            self.frontend_running = True
            self.update_status_card(self.frontend_card, "Работает", self.success_color)
        else:
            self.frontend_running = False
            self.update_status_card(self.frontend_card, "Остановлен", self.error_color)
            
        self.log("Статус обновлён")
        
    def start_backend(self):
        """Запуск backend"""
        if self.backend_running:
            self.log("Backend уже запущен", "WARNING")
            return
            
        def run():
            try:
                backend_dir = self.base_dir / "backend"
                
                # Определяем команду в зависимости от ОС
                if sys.platform == "win32":
                    venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
                    if not venv_python.exists():
                        venv_python = "python"
                else:
                    venv_python = backend_dir / "venv" / "bin" / "python"
                    if not venv_python.exists():
                        venv_python = "python3"
                
                self.log(f"Запуск Backend из {backend_dir}...")
                
                self.backend_process = subprocess.Popen(
                    [str(venv_python), "-m", "uvicorn", "main:app", 
                     "--host", "0.0.0.0", "--port", str(DEFAULT_BACKEND_PORT)],
                    cwd=str(backend_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                
                # Ждём запуска
                time.sleep(3)
                self.root.after(0, self.check_status)
                self.root.after(0, lambda: self.log("Backend запущен", "SUCCESS"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Ошибка запуска Backend: {e}", "ERROR"))
                
        threading.Thread(target=run, daemon=True).start()
        
    def stop_backend(self):
        """Остановка backend"""
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process = None
            
        # Также пробуем убить процесс на порту
        if sys.platform == "win32":
            try:
                subprocess.run(f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{DEFAULT_BACKEND_PORT}') do taskkill /F /PID %a",
                             shell=True, capture_output=True)
            except:
                pass
        else:
            try:
                subprocess.run(f"fuser -k {DEFAULT_BACKEND_PORT}/tcp", shell=True, capture_output=True)
            except:
                pass
                
        time.sleep(1)
        self.check_status()
        self.log("Backend остановлен", "SUCCESS")
        
    def start_frontend(self):
        """Запуск frontend"""
        if self.frontend_running:
            self.log("Frontend уже запущен", "WARNING")
            return
            
        def run():
            try:
                frontend_dir = self.base_dir / "frontend"
                
                # Определяем команду
                if sys.platform == "win32":
                    npx_cmd = "npx.cmd"
                    pnpm_cmd = "pnpm.cmd"
                else:
                    npx_cmd = "npx"
                    pnpm_cmd = "pnpm"
                
                self.log(f"Запуск Frontend из {frontend_dir}...")
                
                # Пробуем pnpm preview
                self.frontend_process = subprocess.Popen(
                    [pnpm_cmd, "preview", "--host", "0.0.0.0", "--port", str(DEFAULT_FRONTEND_PORT)],
                    cwd=str(frontend_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True if sys.platform == "win32" else False,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                
                # Ждём запуска
                time.sleep(3)
                self.root.after(0, self.check_status)
                self.root.after(0, lambda: self.log("Frontend запущен", "SUCCESS"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Ошибка запуска Frontend: {e}", "ERROR"))
                
        threading.Thread(target=run, daemon=True).start()
        
    def stop_frontend(self):
        """Остановка frontend"""
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process = None
            
        # Также пробуем убить процесс на порту
        if sys.platform == "win32":
            try:
                subprocess.run(f"for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :{DEFAULT_FRONTEND_PORT}') do taskkill /F /PID %a",
                             shell=True, capture_output=True)
            except:
                pass
        else:
            try:
                subprocess.run(f"fuser -k {DEFAULT_FRONTEND_PORT}/tcp", shell=True, capture_output=True)
            except:
                pass
                
        time.sleep(1)
        self.check_status()
        self.log("Frontend остановлен", "SUCCESS")
        
    def start_all(self):
        """Запуск всех сервисов"""
        self.log("Запуск всех сервисов...")
        self.start_backend()
        self.root.after(3000, self.start_frontend)
        
    def stop_all(self):
        """Остановка всех сервисов"""
        self.log("Остановка всех сервисов...")
        self.stop_frontend()
        self.stop_backend()
        
    def open_browser(self):
        """Открытие браузера"""
        url = f"http://localhost:{DEFAULT_FRONTEND_PORT}"
        webbrowser.open(url)
        self.log(f"Открыт браузер: {url}")
        
    def on_closing(self):
        """Обработка закрытия приложения"""
        if self.backend_running or self.frontend_running:
            if messagebox.askyesno("Выход", "Сервисы всё ещё работают. Остановить их перед выходом?"):
                self.stop_all()
                time.sleep(2)
        self.root.destroy()


def main():
    root = tk.Tk()
    
    # Устанавливаем иконку если есть
    try:
        if sys.platform == "win32":
            root.iconbitmap("icon.ico")
    except:
        pass
    
    app = SEOMonsterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
