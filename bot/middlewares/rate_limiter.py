import time
from typing import Dict, Tuple, Callable, Any, Optional
from telegram import Update
from telegram.ext import CallbackContext


class RateLimiter:
    """Middleware для ограничения частоты запросов к боту"""
    
    def __init__(self, rate_limit: int = 5, time_window: int = 60):
        """
        Инициализация ограничителя частоты запросов
        
        :param rate_limit: Максимальное количество запросов
        :param time_window: Временное окно в секундах
        """
        self.user_requests: Dict[int, Tuple[int, float]] = {}  # {user_id: (count, first_request_time)}
        self.rate_limit = rate_limit
        self.time_window = time_window
    
    async def process_update(
        self, update: Update, handler: Callable, context: CallbackContext
    ) -> Optional[Any]:
        """
        Обработка обновления перед вызовом обработчика
        
        :param update: Объект обновления от Telegram
        :param handler: Обработчик, который должен быть вызван
        :param context: Контекст бота
        :return: Результат обработки или None, если запрос ограничен
        """
        # Если update не содержит effective_user, пропускаем
        if not update.effective_user:
            return await handler(update, context)
        
        user_id = update.effective_user.id
        current_time = time.time()
        
        # Проверяем, есть ли запись для данного пользователя
        if user_id in self.user_requests:
            count, first_request_time = self.user_requests[user_id]
            
            # Проверяем, не истекло ли временное окно
            if current_time - first_request_time > self.time_window:
                # Сбрасываем счетчик
                self.user_requests[user_id] = (1, current_time)
            else:
                # Инкрементируем счетчик
                count += 1
                
                # Если превышен лимит, отклоняем запрос
                if count > self.rate_limit:
                    await self._handle_rate_limit(update, context)
                    return None
                
                self.user_requests[user_id] = (count, first_request_time)
        else:
            # Первый запрос от пользователя
            self.user_requests[user_id] = (1, current_time)
        
        # Вызываем обработчик
        return await handler(update, context)
    
    async def _handle_rate_limit(self, update: Update, context: CallbackContext) -> None:
        """
        Обработка превышения лимита запросов
        
        :param update: Объект обновления от Telegram
        :param context: Контекст бота
        """
        if update.callback_query:
            await update.callback_query.answer(
                "Пожалуйста, не нажимайте кнопки так часто. Подождите немного.",
                show_alert=True
            )
        elif update.message:
            await update.message.reply_text(
                "Вы отправляете слишком много сообщений. Пожалуйста, подождите немного."
            ) 