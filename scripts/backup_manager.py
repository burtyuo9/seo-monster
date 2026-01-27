#!/usr/bin/env python3
"""
SEO Monster - Backup & Migration Manager
Полное резервное копирование и миграция на другой сервер
"""

import os
import sys
import json
import shutil
import tarfile
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
import subprocess


class BackupManager:
    """Менеджер резервного копирования и миграции"""
    
    def __init__(self, project_dir: str = None):
        self.project_dir = Path(project_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.backup_dir = self.project_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Директории для бэкапа
        self.backup_paths = [
            "backend/data",           # База данных и данные
            "backend/services/data",  # Сессии и аккаунты
            "backend/knowledge",      # База знаний
            "frontend/dist",          # Собранный frontend (если есть)
            "config",                 # Конфигурации
        ]
        
        # Файлы конфигурации
        self.config_files = [
            "backend/app/core/config.py",
            "docker-compose.yml",
            ".env",
        ]
    
    def create_backup(self, include_code: bool = False, description: str = "") -> str:
        """
        Создание полного бэкапа
        
        Args:
            include_code: Включить исходный код
            description: Описание бэкапа
        
        Returns:
            Путь к архиву бэкапа
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"seo_monster_backup_{timestamp}"
        temp_dir = self.backup_dir / backup_name
        temp_dir.mkdir(exist_ok=True)
        
        print(f"📦 Создание бэкапа: {backup_name}")
        
        # Копируем данные
        for path in self.backup_paths:
            src = self.project_dir / path
            if src.exists():
                dst = temp_dir / path
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"  ✓ {path}")
        
        # Копируем конфиги
        for config in self.config_files:
            src = self.project_dir / config
            if src.exists():
                dst = temp_dir / config
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  ✓ {config}")
        
        # Если нужен код
        if include_code:
            for code_dir in ["backend", "frontend"]:
                src = self.project_dir / code_dir
                if src.exists():
                    dst = temp_dir / code_dir
                    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                        '__pycache__', '*.pyc', 'node_modules', '.git', 'dist', '*.log'
                    ))
                    print(f"  ✓ {code_dir} (код)")
        
        # Создаем метаданные
        metadata = {
            "created_at": datetime.now().isoformat(),
            "description": description,
            "include_code": include_code,
            "version": "1.0.0",
            "paths": self.backup_paths,
            "checksum": None
        }
        
        with open(temp_dir / "backup_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Создаем архив
        archive_path = self.backup_dir / f"{backup_name}.tar.gz"
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(temp_dir, arcname=backup_name)
        
        # Вычисляем контрольную сумму
        checksum = self._calculate_checksum(archive_path)
        
        # Обновляем метаданные с контрольной суммой
        metadata["checksum"] = checksum
        with open(temp_dir / "backup_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Пересоздаем архив с обновленными метаданными
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(temp_dir, arcname=backup_name)
        
        # Удаляем временную директорию
        shutil.rmtree(temp_dir)
        
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Бэкап создан: {archive_path}")
        print(f"   Размер: {size_mb:.2f} MB")
        print(f"   Checksum: {checksum[:16]}...")
        
        return str(archive_path)
    
    def restore_backup(self, backup_path: str, target_dir: str = None) -> bool:
        """
        Восстановление из бэкапа
        
        Args:
            backup_path: Путь к архиву бэкапа
            target_dir: Целевая директория (по умолчанию - текущий проект)
        
        Returns:
            True если успешно
        """
        backup_path = Path(backup_path)
        target_dir = Path(target_dir) if target_dir else self.project_dir
        
        if not backup_path.exists():
            print(f"❌ Файл не найден: {backup_path}")
            return False
        
        print(f"📂 Восстановление из: {backup_path}")
        
        # Распаковываем во временную директорию
        temp_dir = self.backup_dir / "temp_restore"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(temp_dir)
        
        # Находим директорию бэкапа
        backup_dirs = list(temp_dir.iterdir())
        if not backup_dirs:
            print("❌ Архив пуст")
            return False
        
        backup_content = backup_dirs[0]
        
        # Проверяем метаданные
        metadata_file = backup_content / "backup_metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            print(f"   Дата создания: {metadata.get('created_at', 'N/A')}")
            print(f"   Описание: {metadata.get('description', 'N/A')}")
        
        # Восстанавливаем файлы
        for item in backup_content.iterdir():
            if item.name == "backup_metadata.json":
                continue
            
            dst = target_dir / item.name
            
            # Создаем бэкап существующих данных
            if dst.exists():
                backup_existing = target_dir / f"{item.name}.old"
                if backup_existing.exists():
                    shutil.rmtree(backup_existing) if backup_existing.is_dir() else backup_existing.unlink()
                shutil.move(str(dst), str(backup_existing))
            
            # Копируем новые данные
            if item.is_dir():
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)
            
            print(f"  ✓ {item.name}")
        
        # Очищаем временную директорию
        shutil.rmtree(temp_dir)
        
        print(f"\n✅ Восстановление завершено в: {target_dir}")
        return True
    
    def list_backups(self) -> list:
        """Список доступных бэкапов"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            stat = backup_file.stat()
            backups.append({
                "name": backup_file.name,
                "path": str(backup_file),
                "size_mb": stat.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def export_for_migration(self, output_path: str = None) -> str:
        """
        Экспорт для миграции на другой сервер
        Включает все необходимое для полного развертывания
        
        Args:
            output_path: Путь для сохранения архива
        
        Returns:
            Путь к архиву
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_path:
            archive_path = Path(output_path)
        else:
            archive_path = self.backup_dir / f"seo_monster_migration_{timestamp}.tar.gz"
        
        print("🚀 Создание пакета миграции...")
        
        # Создаем полный бэкап с кодом
        temp_dir = self.backup_dir / "migration_temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        # Копируем весь проект
        for item in self.project_dir.iterdir():
            if item.name in ['.git', 'node_modules', '__pycache__', 'backups', '.venv', 'venv']:
                continue
            
            dst = temp_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dst, ignore=shutil.ignore_patterns(
                    '__pycache__', '*.pyc', 'node_modules', '.git', '*.log', '.venv', 'venv'
                ))
            else:
                shutil.copy2(item, dst)
            print(f"  ✓ {item.name}")
        
        # Создаем скрипт установки
        install_script = '''#!/bin/bash
# SEO Monster - Installation Script
# Автоматическая установка на новом сервере

set -e

echo "🚀 SEO Monster - Установка"
echo "=========================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.9+"
    exit 1
fi

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo "⚠️ Node.js не найден. Установка frontend будет пропущена."
    SKIP_FRONTEND=1
fi

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей Python
echo "📦 Установка Python зависимостей..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Установка frontend (если Node.js доступен)
if [ -z "$SKIP_FRONTEND" ]; then
    echo "📦 Установка frontend зависимостей..."
    cd frontend
    npm install
    cd ..
fi

# Создание директорий
mkdir -p backend/data
mkdir -p backend/services/data/sessions
mkdir -p backend/knowledge
mkdir -p logs

# Настройка прав
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x scripts/*.py 2>/dev/null || true

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Для запуска:"
echo "  1. Активируйте окружение: source venv/bin/activate"
echo "  2. Запустите backend: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
echo "  3. Запустите frontend: cd frontend && npm run dev"
echo ""
echo "Или используйте Docker:"
echo "  docker-compose up -d"
'''
        
        with open(temp_dir / "install.sh", "w") as f:
            f.write(install_script)
        os.chmod(temp_dir / "install.sh", 0o755)
        
        # Создаем архив
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(temp_dir, arcname="seo_monster")
        
        # Очищаем
        shutil.rmtree(temp_dir)
        
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Пакет миграции создан: {archive_path}")
        print(f"   Размер: {size_mb:.2f} MB")
        print(f"\n📋 Для миграции на новый сервер:")
        print(f"   1. Скопируйте файл на новый сервер")
        print(f"   2. Распакуйте: tar -xzf {archive_path.name}")
        print(f"   3. Запустите: cd seo_monster && ./install.sh")
        
        return str(archive_path)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Вычисление контрольной суммы файла"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="SEO Monster Backup Manager")
    subparsers = parser.add_subparsers(dest="command", help="Команды")
    
    # Создание бэкапа
    backup_parser = subparsers.add_parser("backup", help="Создать бэкап")
    backup_parser.add_argument("--include-code", action="store_true", help="Включить исходный код")
    backup_parser.add_argument("--description", "-d", default="", help="Описание бэкапа")
    
    # Восстановление
    restore_parser = subparsers.add_parser("restore", help="Восстановить из бэкапа")
    restore_parser.add_argument("backup_path", help="Путь к файлу бэкапа")
    restore_parser.add_argument("--target", "-t", help="Целевая директория")
    
    # Список бэкапов
    subparsers.add_parser("list", help="Список бэкапов")
    
    # Миграция
    migrate_parser = subparsers.add_parser("migrate", help="Создать пакет для миграции")
    migrate_parser.add_argument("--output", "-o", help="Путь для сохранения")
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.command == "backup":
        manager.create_backup(
            include_code=args.include_code,
            description=args.description
        )
    elif args.command == "restore":
        manager.restore_backup(args.backup_path, args.target)
    elif args.command == "list":
        backups = manager.list_backups()
        if backups:
            print("\n📋 Доступные бэкапы:\n")
            for b in backups:
                print(f"  📦 {b['name']}")
                print(f"     Размер: {b['size_mb']:.2f} MB")
                print(f"     Создан: {b['created']}")
                print()
        else:
            print("Нет доступных бэкапов")
    elif args.command == "migrate":
        manager.export_for_migration(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
