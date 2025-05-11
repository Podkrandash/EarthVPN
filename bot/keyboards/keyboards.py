from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict, Any, Optional

class Keyboards:
    @staticmethod
    def start_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура приветственного сообщения"""
        keyboard = [
            [InlineKeyboardButton("🚀 Начать", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def main_menu_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура главного меню"""
        keyboard = [
            [InlineKeyboardButton("🌐 О сервисе", callback_data="about")],
            [InlineKeyboardButton("💎 Тарифы и подписка", callback_data="tariffs")],
            [InlineKeyboardButton("❓ FAQ", callback_data="faq")],
            [InlineKeyboardButton("🛡 Поддержка", callback_data="support")],
            [InlineKeyboardButton("👤 Личный кабинет", callback_data="profile")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_keyboard(destination: str = "main_menu") -> InlineKeyboardMarkup:
        """Клавиатура с кнопкой назад"""
        keyboard = [
            [InlineKeyboardButton("◀️ Назад", callback_data=destination)]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def tariffs_keyboard(tariffs: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Клавиатура для выбора тарифа"""
        keyboard = []
        for tariff in tariffs:
            keyboard.append([
                InlineKeyboardButton(
                    f"{tariff['name']} - {tariff['price']} руб.",
                    callback_data=f"tariff_{tariff['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def tariff_info_keyboard(tariff_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для конкретного тарифа"""
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить", callback_data=f"pay_{tariff_id}")],
            [InlineKeyboardButton("◀️ Назад", callback_data="tariffs")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_methods_keyboard(tariff_id: int, payment_methods: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        """Клавиатура для выбора способа оплаты"""
        keyboard = []
        for method in payment_methods:
            keyboard.append([
                InlineKeyboardButton(
                    method['name'],
                    callback_data=f"payment_method_{method['id']}_{tariff_id}"
                )
            ])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data=f"tariff_{tariff_id}")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def profile_keyboard(has_subscription: bool) -> InlineKeyboardMarkup:
        """Клавиатура для личного кабинета"""
        keyboard = []
        if has_subscription:
            keyboard.append([InlineKeyboardButton("📋 Скачать конфигурации", callback_data="configs")])
            keyboard.append([InlineKeyboardButton("🔄 Продлить подписку", callback_data="tariffs")])
        else:
            keyboard.append([InlineKeyboardButton("🛒 Выбрать тариф", callback_data="tariffs")])
        
        keyboard.append([InlineKeyboardButton("📊 История покупок", callback_data="payment_history")])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def configs_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для выбора типа конфигурации"""
        keyboard = [
            [InlineKeyboardButton("OpenVPN", callback_data="config_openvpn")],
            [InlineKeyboardButton("WireGuard", callback_data="config_wireguard")],
            [InlineKeyboardButton("◀️ Назад", callback_data="profile")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def faq_keyboard(faq_items: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        """Клавиатура для FAQ вопросов"""
        keyboard = []
        for i, item in enumerate(faq_items):
            keyboard.append([
                InlineKeyboardButton(
                    item['question'],
                    callback_data=f"faq_item_{i}"
                )
            ])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def faq_item_keyboard(item_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для отдельного вопроса FAQ"""
        keyboard = [
            [InlineKeyboardButton("◀️ Назад", callback_data="faq")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def admin_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для панели администратора"""
        keyboard = [
            [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("💰 Управление тарифами", callback_data="admin_tariffs")],
            [InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def admin_users_keyboard(page: int = 0, total_pages: int = 0) -> InlineKeyboardMarkup:
        """Клавиатура для просмотра пользователей с пагинацией"""
        keyboard = []
        
        # Навигация по страницам
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"admin_users_page_{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages+1}", callback_data="ignore"))
        
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"admin_users_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
            
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="admin")])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def check_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
        """Клавиатура для проверки статуса платежа"""
        keyboard = [
            [InlineKeyboardButton("🔄 Проверить оплату", callback_data=f"check_payment_{payment_id}")],
            [InlineKeyboardButton("❌ Отменить", callback_data="tariffs")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_history_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для истории платежей"""
        keyboard = [
            [InlineKeyboardButton("◀️ Назад", callback_data="profile")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def support_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для поддержки"""
        keyboard = [
            [InlineKeyboardButton("📨 Написать в поддержку", url="https://t.me/earthvpn_support")],
            [InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard) 