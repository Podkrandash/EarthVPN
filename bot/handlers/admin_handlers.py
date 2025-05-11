from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from typing import List, Dict, Any, Optional
import datetime

from bot.keyboards.keyboards import Keyboards
from config.config import ADMIN_IDS, TARIFFS
from database.models import DatabaseManager


class AdminHandlers:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.ITEMS_PER_PAGE = 5  # Количество элементов на странице для пагинации

    async def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        return user_id in ADMIN_IDS

    async def admin_panel(self, update: Update, context: CallbackContext) -> None:
        """Обработчик административной панели"""
        user = update.effective_user
        
        if not await self.is_admin(user.id):
            await context.bot.send_message(
                chat_id=user.id,
                text="⛔ У вас нет доступа к административной панели"
            )
            return
        
        await context.bot.send_message(
            chat_id=user.id,
            text="🔑 <b>Административная панель</b>\n\nВыберите раздел:",
            reply_markup=Keyboards.admin_keyboard(),
            parse_mode="HTML"
        )

    async def admin_users(self, update: Update, context: CallbackContext) -> None:
        """Обработчик списка пользователей"""
        query = update.callback_query
        user = update.effective_user
        
        if not await self.is_admin(user.id):
            await query.answer("⛔ У вас нет доступа к этому разделу")
            return
        
        # Определяем номер страницы
        page = 0
        if query.data.startswith("admin_users_page_"):
            page = int(query.data.split("_")[-1])
        
        # Получаем всех пользователей
        users = await self.db_manager.get_all_users()
        
        # Вычисляем общее количество страниц
        total_pages = len(users) // self.ITEMS_PER_PAGE
        if len(users) % self.ITEMS_PER_PAGE > 0:
            total_pages += 1
        total_pages = max(0, total_pages - 1)
        
        # Получаем пользователей для текущей страницы
        start_idx = page * self.ITEMS_PER_PAGE
        end_idx = min(start_idx + self.ITEMS_PER_PAGE, len(users))
        page_users = users[start_idx:end_idx]
        
        # Формируем текст сообщения
        text = f"👥 <b>Пользователи</b> (всего: {len(users)})\n\n"
        
        for idx, user_data in enumerate(page_users, start=start_idx+1):
            reg_date = datetime.datetime.strptime(user_data["registration_date"], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y")
            username = user_data["username"] or "Нет"
            name = f"{user_data['first_name']} {user_data['last_name']}".strip() or "Не указано"
            
            text += f"{idx}. ID: <code>{user_data['user_id']}</code>\n"
            text += f"👤 {name} (@{username})\n"
            text += f"📅 Зарегистрирован: {reg_date}\n\n"
        
        # Если пользователей нет
        if not page_users:
            text += "Пользователи не найдены"
        
        # Отправляем сообщение с пагинацией
        await query.edit_message_text(
            text=text,
            reply_markup=Keyboards.admin_users_keyboard(page, total_pages),
            parse_mode="HTML"
        )

    async def admin_stats(self, update: Update, context: CallbackContext) -> None:
        """Обработчик статистики"""
        query = update.callback_query
        user = update.effective_user
        
        if not await self.is_admin(user.id):
            await query.answer("⛔ У вас нет доступа к этому разделу")
            return
        
        # Получаем всех пользователей
        users = await self.db_manager.get_all_users()
        
        # Получаем статистику по тарифам
        subscriptions = []
        for u in users:
            sub = await self.db_manager.get_active_subscription(u["user_id"])
            if sub:
                subscriptions.append(sub)
        
        # Группируем подписки по тарифам
        tariff_stats = {}
        for sub in subscriptions:
            tariff_id = sub["tariff_id"]
            if tariff_id in tariff_stats:
                tariff_stats[tariff_id] += 1
            else:
                tariff_stats[tariff_id] = 1
        
        # Формируем текст сообщения
        now = datetime.datetime.now()
        today = now.strftime("%d.%m.%Y")
        
        text = f"📊 <b>Статистика на {today}</b>\n\n"
        text += f"👥 Всего пользователей: {len(users)}\n"
        text += f"💰 Активных подписок: {len(subscriptions)}\n\n"
        
        if tariff_stats:
            text += "<b>По тарифам:</b>\n"
            for tariff_id, count in tariff_stats.items():
                tariff = next((t for t in TARIFFS if t["id"] == tariff_id), None)
                if tariff:
                    text += f"• {tariff['name']}: {count} подписчиков\n"
        
        # Отправляем сообщение
        await query.edit_message_text(
            text=text,
            reply_markup=Keyboards.back_keyboard("admin"),
            parse_mode="HTML"
        )

    async def admin_tariffs(self, update: Update, context: CallbackContext) -> None:
        """Обработчик управления тарифами"""
        query = update.callback_query
        user = update.effective_user
        
        if not await self.is_admin(user.id):
            await query.answer("⛔ У вас нет доступа к этому разделу")
            return
        
        # Формируем текст сообщения со списком тарифов
        text = "💰 <b>Управление тарифами</b>\n\n"
        
        for tariff in TARIFFS:
            text += f"<b>{tariff['name']}</b>\n"
            text += f"Цена: {tariff['price']} руб.\n"
            text += f"Длительность: {tariff['duration_days']} дней\n"
            text += f"Устройств: {tariff['device_count']}\n\n"
        
        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("➕ Добавить тариф", callback_data="admin_add_tariff")],
            [InlineKeyboardButton("✏️ Редактировать тариф", callback_data="admin_edit_tariff")],
            [InlineKeyboardButton("❌ Удалить тариф", callback_data="admin_delete_tariff")],
            [InlineKeyboardButton("◀️ Назад", callback_data="admin")]
        ]
        
        # Отправляем сообщение
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    async def admin_broadcast(self, update: Update, context: CallbackContext) -> None:
        """Обработчик рассылки сообщений"""
        query = update.callback_query
        user = update.effective_user
        
        if not await self.is_admin(user.id):
            await query.answer("⛔ У вас нет доступа к этому разделу")
            return
        
        # Устанавливаем состояние ожидания текста рассылки
        context.user_data["waiting_for_broadcast"] = True
        
        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("❌ Отмена", callback_data="admin")]
        ]
        
        # Отправляем сообщение
        await query.edit_message_text(
            text="📨 <b>Рассылка сообщений</b>\n\nВведите текст для рассылки всем пользователям:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    async def process_broadcast_message(self, update: Update, context: CallbackContext) -> None:
        """Обработчик ввода текста для рассылки"""
        user = update.effective_user
        message = update.message.text
        
        if not await self.is_admin(user.id):
            await update.message.reply_text("⛔ У вас нет доступа к этой функции")
            return
        
        if "waiting_for_broadcast" not in context.user_data or not context.user_data["waiting_for_broadcast"]:
            return
        
        # Сбрасываем состояние ожидания
        context.user_data["waiting_for_broadcast"] = False
        
        # Получаем всех пользователей
        users = await self.db_manager.get_all_users()
        
        # Отправляем подтверждение администратору
        await update.message.reply_text(
            f"✅ Рассылка сообщения {len(users)} пользователям начата...",
            reply_markup=Keyboards.back_keyboard("admin")
        )
        
        # Отправляем сообщение всем пользователям
        success_count = 0
        for u in users:
            try:
                await context.bot.send_message(
                    chat_id=u["user_id"],
                    text=f"📢 <b>Уведомление от EarthVPN</b>\n\n{message}",
                    parse_mode="HTML"
                )
                success_count += 1
            except Exception:
                # Игнорируем ошибки отправки
                pass
        
        # Отправляем отчет администратору
        await context.bot.send_message(
            chat_id=user.id,
            text=f"✅ Рассылка завершена\nОтправлено: {success_count} из {len(users)} пользователей",
            reply_markup=Keyboards.back_keyboard("admin"),
            parse_mode="HTML"
        ) 