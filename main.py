import os
import logging
import sys
from typing import Dict, Any, Optional
import asyncio

from telegram import Update, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from config.config import BOT_TOKEN, DATABASE_PATH, ADMIN_IDS
from database.models import DatabaseManager
from bot.handlers.base_handlers import BaseHandlers
from bot.handlers.admin_handlers import AdminHandlers
from bot.services.vpn_service import VPNService


# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def error_handler(update: Optional[object], context: CallbackContext) -> None:
    """Обработчик ошибок бота."""
    logger.error("Произошла ошибка: %s", context.error, exc_info=context.error)


class EarthVPNBot:
    """Основной класс бота EarthVPN"""
    
    def __init__(self, token: str, db_path: str):
        """Инициализация бота"""
        self.token = token
        self.db_manager = DatabaseManager(db_path)
        self.base_handlers = BaseHandlers(self.db_manager)
        self.admin_handlers = AdminHandlers(self.db_manager)
        self.vpn_service = VPNService()
        
        # Инициализация бота для v13.x
        self.updater = Updater(token=token, use_context=True, request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
        self.dispatcher = self.updater.dispatcher
        
        # Регистрация обработчиков
        self._register_handlers()
        
        # Регистрация обработчика ошибок
        self.dispatcher.add_error_handler(error_handler)
    
    def _register_handlers(self) -> None:
        """Регистрация обработчиков команд и сообщений"""
        # Команды
        self.dispatcher.add_handler(CommandHandler("start", self.base_handlers.start))
        self.dispatcher.add_handler(CommandHandler("admin", self.admin_handlers.admin_panel))
        
        # Обработчики callback-запросов (меню)
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.main_menu, pattern="^main_menu$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.about, pattern="^about$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.tariffs, pattern="^tariffs$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.faq, pattern="^faq$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.support, pattern="^support$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.profile, pattern="^profile$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.tariff_info, pattern="^tariff_"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.faq_item, pattern="^faq_item_"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.payment, pattern="^pay_"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.process_payment_method, pattern="^payment_method_"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.check_payment, pattern="^check_payment_"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.configs, pattern="^configs$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.download_config, pattern="^config_"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.base_handlers.payment_history, pattern="^payment_history$"
        ))
        
        # Админские обработчики
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.admin_handlers.admin_panel, pattern="^admin$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.admin_handlers.admin_users, pattern="^admin_users"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.admin_handlers.admin_stats, pattern="^admin_stats$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.admin_handlers.admin_tariffs, pattern="^admin_tariffs$"
        ))
        self.dispatcher.add_handler(CallbackQueryHandler(
            self.admin_handlers.admin_broadcast, pattern="^admin_broadcast$"
        ))
        
        # Обработчик для текстовых сообщений (например, для рассылки админом)
        self.dispatcher.add_handler(MessageHandler(
            Filters.text & ~Filters.command, self.process_text_message
        ))
    
    def process_text_message(self, update: Update, context: CallbackContext) -> None:
        """Обработчик текстовых сообщений"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Запускаем асинхронную функцию
        loop.run_until_complete(self._process_text_message_async(update, context))
    
    async def _process_text_message_async(self, update: Update, context: CallbackContext) -> None:
        """Асинхронная реализация обработчика текстовых сообщений"""
        user = update.effective_user
        
        # Проверяем, является ли это вводом текста для рассылки
        if user.id in ADMIN_IDS and context.user_data.get("waiting_for_broadcast"):
            await self.admin_handlers.process_broadcast_message(update, context)
        else:
            # Отправляем пользователя в главное меню, если он отправляет текст
            # Удаляем await перед update.message.reply_text
            update.message.reply_text(
                "Пожалуйста, используйте меню для навигации. Отправьте /start чтобы начать заново."
            )
    
    def run(self) -> None:
        """Запуск бота в цикле событий"""
        self.updater.start_polling()
        logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
        self.updater.idle()


if __name__ == "__main__":
    # Проверяем наличие токена
    if not BOT_TOKEN:
        logger.error("Ошибка: Токен бота не найден. Укажите BOT_TOKEN в .env файле.")
        sys.exit(1)

    # Получаем или создаем цикл событий asyncio
    # try:
    #     loop = asyncio.get_event_loop()
    # except RuntimeError:
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)

    # Создаем и запускаем бота
    bot = EarthVPNBot(BOT_TOKEN, DATABASE_PATH)
    
    try:
        # Возвращаем стандартный вызов run()
        logger.info("Запуск бота...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка: {e}", exc_info=True)
    finally:
        if bot.updater.running:
            bot.updater.stop()
            logger.info("Updater остановлен.")
        logger.info("Завершение работы бота.") 