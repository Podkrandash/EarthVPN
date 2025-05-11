import sqlite3
import aiosqlite
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union


class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных при первом запуске"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Таблица подписок
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tariff_id INTEGER,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')

        # Таблица платежей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            tariff_id INTEGER,
            amount REAL,
            payment_method TEXT,
            payment_id TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')

        # Таблица конфигурационных файлов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            config_type TEXT,
            config_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')

        conn.commit()
        conn.close()

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ) as cursor:
                user = await cursor.fetchone()
                if user:
                    return dict(user)
                return None

    async def add_user(self, user_id: int, username: str, first_name: str, last_name: str) -> bool:
        """Добавить нового пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """
                    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, username, first_name, last_name),
                )
                await db.commit()
                return True
            except Exception:
                return False

    async def update_user_activity(self, user_id: int) -> bool:
        """Обновить время последней активности пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,),
                )
                await db.commit()
                return True
            except Exception:
                return False

    async def get_active_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить активную подписку пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM subscriptions 
                WHERE user_id = ? AND is_active = 1 AND end_date > CURRENT_TIMESTAMP
                ORDER BY end_date DESC LIMIT 1
                """,
                (user_id,),
            ) as cursor:
                subscription = await cursor.fetchone()
                if subscription:
                    return dict(subscription)
                return None

    async def add_subscription(self, user_id: int, tariff_id: int, duration_days: int) -> int:
        """Добавить новую подписку"""
        end_date = (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO subscriptions (user_id, tariff_id, end_date)
                VALUES (?, ?, ?)
                """,
                (user_id, tariff_id, end_date),
            )
            await db.commit()
            return cursor.lastrowid

    async def deactivate_subscription(self, subscription_id: int) -> bool:
        """Деактивировать подписку"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "UPDATE subscriptions SET is_active = 0 WHERE id = ?",
                    (subscription_id,),
                )
                await db.commit()
                return True
            except Exception:
                return False

    async def create_payment(
        self, user_id: int, tariff_id: int, amount: float, payment_method: str
    ) -> int:
        """Создать новую запись о платеже"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO payments (user_id, tariff_id, amount, payment_method, status)
                VALUES (?, ?, ?, ?, 'pending')
                """,
                (user_id, tariff_id, amount, payment_method),
            )
            await db.commit()
            return cursor.lastrowid

    async def update_payment(self, payment_id: int, payment_external_id: str, status: str) -> bool:
        """Обновить статус платежа"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    """
                    UPDATE payments 
                    SET payment_id = ?, status = ?
                    WHERE id = ?
                    """,
                    (payment_external_id, status, payment_id),
                )
                await db.commit()
                return True
            except Exception:
                return False

    async def get_payment(self, payment_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о платеже"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM payments WHERE id = ?", (payment_id,)
            ) as cursor:
                payment = await cursor.fetchone()
                if payment:
                    return dict(payment)
                return None

    async def save_config(self, user_id: int, config_type: str, config_data: Dict) -> int:
        """Сохранить конфигурационный файл пользователя"""
        config_json = json.dumps(config_data)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO configs (user_id, config_type, config_data)
                VALUES (?, ?, ?)
                """,
                (user_id, config_type, config_json),
            )
            await db.commit()
            return cursor.lastrowid

    async def get_configs(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все конфигурационные файлы пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            configs = []
            async with db.execute(
                "SELECT * FROM configs WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
            ) as cursor:
                async for row in cursor:
                    config = dict(row)
                    config["config_data"] = json.loads(config["config_data"])
                    configs.append(config)
            return configs

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Получить список всех пользователей (для админки)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            users = []
            async with db.execute("SELECT * FROM users ORDER BY registration_date DESC") as cursor:
                async for row in cursor:
                    users.append(dict(row))
            return users

    async def get_user_subscriptions(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все подписки пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            subscriptions = []
            async with db.execute(
                "SELECT * FROM subscriptions WHERE user_id = ? ORDER BY start_date DESC", (user_id,)
            ) as cursor:
                async for row in cursor:
                    subscriptions.append(dict(row))
            return subscriptions

    async def get_user_payments(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все платежи пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            payments = []
            async with db.execute(
                "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
            ) as cursor:
                async for row in cursor:
                    payments.append(dict(row))
            return payments 