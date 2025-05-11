from telegram import Update, Message
from telegram.ext import CallbackContext
from typing import Optional, Dict, Any, List, Union
import datetime
import asyncio  # Добавляем импорт asyncio

from bot.keyboards.keyboards import Keyboards
from config.config import MESSAGES, TARIFFS, FAQ_ITEMS, PAYMENT_METHODS
from database.models import DatabaseManager


class BaseHandlers:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.user_message_ids = {}  # Для хранения ID сообщений пользователей

    async def save_user_message_id(self, user_id: int, message_id: int) -> None:
        """Сохранить ID последнего сообщения от бота пользователю"""
        # Удаляем старые сообщения перед сохранением нового
        if user_id in self.user_message_ids:
            self.user_message_ids[user_id].append(message_id)
        else:
            self.user_message_ids[user_id] = [message_id]

    async def delete_previous_messages(self, update: Update, context: CallbackContext) -> None:
        """Удалить предыдущие сообщения бота пользователю"""
        user_id = update.effective_user.id
        
        if user_id in self.user_message_ids:
            for message_id in self.user_message_ids[user_id]:
                try:
                    context.bot.delete_message(chat_id=user_id, message_id=message_id)
                except Exception:
                    pass  # Игнорируем ошибки при удалении сообщений
            
            # Очищаем список после удаления
            self.user_message_ids[user_id] = []

    async def send_message_and_save_id(
        self, update: Update, context: CallbackContext, text: str, keyboard=None
    ) -> Message:
        """Отправить сообщение и сохранить его ID"""
        # Удаляем старые сообщения
        await self.delete_previous_messages(update, context)
        
        # Отправляем новое сообщение
        message = context.bot.send_message(
            chat_id=update.effective_user.id,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Сохраняем ID нового сообщения
        await self.save_user_message_id(update.effective_user.id, message.message_id)
        
        return message

    async def _start_async(self, update: Update, context: CallbackContext) -> None:
        """Внутренняя асинхронная реализация обработчика команды /start"""
        user = update.effective_user
        
        # Добавляем пользователя в базу данных
        await self.db_manager.add_user(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or ""
        )
        
        # Отправляем приветственное сообщение
        context.bot.send_message(
            chat_id=user.id,
            text=MESSAGES["start"],
            reply_markup=Keyboards.start_keyboard(),
            parse_mode="HTML"
        )
        
        # Обновляем время последней активности
        await self.db_manager.update_user_activity(user.id)

    def start(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /start - синхронная обертка для асинхронной функции"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Запускаем асинхронную функцию в цикле событий
        loop.run_until_complete(self._start_async(update, context))

    def main_menu(self, update: Update, context: CallbackContext) -> None:
        """Обработчик главного меню"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Запускаем асинхронную функцию
        loop.run_until_complete(self._main_menu_async(update, context))
        
    async def _main_menu_async(self, update: Update, context: CallbackContext) -> None:
        """Асинхронная реализация обработчика главного меню"""
        user = update.effective_user
        
        # Отправляем сообщение с главным меню
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=MESSAGES["main_menu"],
            keyboard=Keyboards.main_menu_keyboard()
        )
        
        # Обновляем время последней активности
        await self.db_manager.update_user_activity(user.id)

    def about(self, update: Update, context: CallbackContext) -> None:
        """Обработчик раздела 'О сервисе'"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Запускаем асинхронную функцию
        loop.run_until_complete(self._about_async(update, context))
        
    async def _about_async(self, update: Update, context: CallbackContext) -> None:
        """Асинхронная реализация обработчика раздела 'О сервисе'"""
        user = update.effective_user
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=MESSAGES["about"],
            keyboard=Keyboards.back_keyboard()
        )
        
        await self.db_manager.update_user_activity(user.id)

    def tariffs(self, update: Update, context: CallbackContext) -> None:
        """Обработчик раздела 'Тарифы и подписка'"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Запускаем асинхронную функцию
        loop.run_until_complete(self._tariffs_async(update, context))
        
    async def _tariffs_async(self, update: Update, context: CallbackContext) -> None:
        """Асинхронная реализация обработчика раздела 'Тарифы и подписка'"""
        user = update.effective_user
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=MESSAGES["tariffs"],
            keyboard=Keyboards.tariffs_keyboard(TARIFFS)
        )
        
        await self.db_manager.update_user_activity(user.id)

    def tariff_info(self, update: Update, context: CallbackContext) -> None:
        """Обработчик информации о конкретном тарифе"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Запускаем асинхронную функцию
        loop.run_until_complete(self._tariff_info_async(update, context))
        
    async def _tariff_info_async(self, update: Update, context: CallbackContext) -> None:
        """Асинхронная реализация обработчика информации о конкретном тарифе"""
        query = update.callback_query
        tariff_id = int(query.data.split('_')[1])
        user = update.effective_user
        
        # Находим тариф по ID
        tariff = next((t for t in TARIFFS if t["id"] == tariff_id), None)
        
        if tariff:
            # Форматируем список стран
            countries_text = ", ".join(tariff["countries"]) if len(tariff["countries"]) < 5 else f"{len(tariff['countries'])} стран"
            
            # Формируем текст сообщения
            text = MESSAGES["tariff_info"].format(
                name=tariff["name"],
                description=tariff["description"],
                price=tariff["price"],
                duration_days=tariff["duration_days"],
                device_count=tariff["device_count"],
                countries=countries_text
            )
            
            await self.send_message_and_save_id(
                update=update,
                context=context,
                text=text,
                keyboard=Keyboards.tariff_info_keyboard(tariff_id)
            )
        
        await self.db_manager.update_user_activity(user.id)

    def faq(self, update: Update, context: CallbackContext) -> None:
        """Обработчик раздела 'FAQ'"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Запускаем асинхронную функцию
        loop.run_until_complete(self._faq_async(update, context))
        
    async def _faq_async(self, update: Update, context: CallbackContext) -> None:
        """Асинхронная реализация обработчика раздела 'FAQ'"""
        user = update.effective_user
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=MESSAGES["faq"],
            keyboard=Keyboards.faq_keyboard(FAQ_ITEMS)
        )
        
        await self.db_manager.update_user_activity(user.id)

    def faq_item(self, update: Update, context: CallbackContext) -> None:
        """Обработчик конкретного вопроса FAQ"""
        # Получаем или создаем цикл событий
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Запускаем асинхронную функцию
        loop.run_until_complete(self._faq_item_async(update, context))
        
    async def _faq_item_async(self, update: Update, context: CallbackContext) -> None:
        """Асинхронная реализация обработчика конкретного вопроса FAQ"""
        query = update.callback_query
        item_id = int(query.data.split('_')[2])
        user = update.effective_user
        
        if 0 <= item_id < len(FAQ_ITEMS):
            item = FAQ_ITEMS[item_id]
            text = f"<b>Вопрос:</b> {item['question']}\n\n<b>Ответ:</b> {item['answer']}"
            
            await self.send_message_and_save_id(
                update=update,
                context=context,
                text=text,
                keyboard=Keyboards.faq_item_keyboard(item_id)
            )
        
        await self.db_manager.update_user_activity(user.id)

    async def support(self, update: Update, context: CallbackContext) -> None:
        """Обработчик раздела 'Поддержка'"""
        user = update.effective_user
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=MESSAGES["support"],
            keyboard=Keyboards.support_keyboard()
        )
        
        await self.db_manager.update_user_activity(user.id)

    async def profile(self, update: Update, context: CallbackContext) -> None:
        """Обработчик личного кабинета пользователя"""
        user = update.effective_user
        
        # Получаем активную подписку пользователя
        subscription = await self.db_manager.get_active_subscription(user.id)
        
        if subscription:
            # Находим тариф по ID
            tariff = next((t for t in TARIFFS if t["id"] == subscription["tariff_id"]), None)
            
            if tariff:
                # Форматируем дату окончания подписки
                end_date = datetime.datetime.strptime(subscription["end_date"], "%Y-%m-%d %H:%M:%S")
                days_left = (end_date - datetime.datetime.now()).days
                
                # Формируем информацию о профиле
                profile_info = MESSAGES["subscription_info"].format(
                    tariff_name=tariff["name"],
                    expire_date=end_date.strftime("%d.%m.%Y"),
                    days_left=max(0, days_left)
                )
            else:
                profile_info = MESSAGES["no_subscription"]
        else:
            profile_info = MESSAGES["no_subscription"]
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=MESSAGES["profile"].format(profile_info=profile_info),
            keyboard=Keyboards.profile_keyboard(bool(subscription))
        )
        
        await self.db_manager.update_user_activity(user.id)

    async def payment(self, update: Update, context: CallbackContext) -> None:
        """Обработчик оплаты"""
        query = update.callback_query
        tariff_id = int(query.data.split('_')[1])
        user = update.effective_user
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=MESSAGES["payment"],
            keyboard=Keyboards.payment_methods_keyboard(tariff_id, PAYMENT_METHODS)
        )
        
        await self.db_manager.update_user_activity(user.id)

    async def process_payment_method(self, update: Update, context: CallbackContext) -> None:
        """Обработчик выбора способа оплаты"""
        query = update.callback_query
        parts = query.data.split('_')
        method_id = parts[2]
        tariff_id = int(parts[3])
        user = update.effective_user
        
        # Находим тариф по ID
        tariff = next((t for t in TARIFFS if t["id"] == tariff_id), None)
        
        if not tariff:
            await self.send_message_and_save_id(
                update=update, 
                context=context,
                text="Тариф не найден. Пожалуйста, выберите другой тариф.",
                keyboard=Keyboards.back_keyboard("tariffs")
            )
            return
        
        # Создаем запись о платеже в базе данных
        payment_id = await self.db_manager.create_payment(
            user_id=user.id,
            tariff_id=tariff_id,
            amount=tariff["price"],
            payment_method=method_id
        )
        
        # Здесь должна быть интеграция с платежной системой
        # В данном примере просто показываем информацию для оплаты
        
        # Имитация платежной системы
        payment_info = f"<b>Оплата тарифа:</b> {tariff['name']}\n"
        payment_info += f"<b>Сумма:</b> {tariff['price']} руб.\n\n"
        
        if method_id == "card":
            payment_info += "Для оплаты картой перейдите по ссылке: <a href='https://example.com/pay'>Оплатить</a>"
        elif method_id == "crypto":
            payment_info += "Отправьте Bitcoin на адрес: <code>bc1q...</code>"
        elif method_id == "qiwi":
            payment_info += "Номер QIWI кошелька: <code>+79XXXXXXXXX</code>"
        elif method_id == "yoomoney":
            payment_info += "Номер ЮMoney: <code>41001XXXXXXXXX</code>"
        
        payment_info += "\n\nПосле оплаты нажмите кнопку 'Проверить оплату'"
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=payment_info,
            keyboard=Keyboards.check_payment_keyboard(payment_id)
        )
        
        await self.db_manager.update_user_activity(user.id)

    async def check_payment(self, update: Update, context: CallbackContext) -> None:
        """Обработчик проверки статуса платежа"""
        query = update.callback_query
        payment_id = int(query.data.split('_')[2])
        user = update.effective_user
        
        # Получаем информацию о платеже
        payment = await self.db_manager.get_payment(payment_id)
        
        if not payment:
            await self.send_message_and_save_id(
                update=update,
                context=context,
                text="Платеж не найден. Пожалуйста, попробуйте снова.",
                keyboard=Keyboards.back_keyboard("tariffs")
            )
            return
        
        # В реальном проекте здесь должна быть проверка через API платежной системы
        # В данном примере, для демонстрации, считаем платеж успешным
        
        # Имитация успешного платежа
        if payment["status"] == "pending":
            # Обновляем статус платежа
            await self.db_manager.update_payment(
                payment_id=payment_id,
                payment_external_id="test_payment_id",
                status="success"
            )
            
            # Находим тариф по ID
            tariff = next((t for t in TARIFFS if t["id"] == payment["tariff_id"]), None)
            
            if tariff:
                # Добавляем подписку пользователю
                subscription_id = await self.db_manager.add_subscription(
                    user_id=user.id,
                    tariff_id=tariff["id"],
                    duration_days=tariff["duration_days"]
                )
                
                # Генерируем конфигурационные файлы (в реальном проекте)
                await self.generate_config_files(user.id, tariff)
                
                await self.send_message_and_save_id(
                    update=update,
                    context=context,
                    text=f"✅ Оплата успешно произведена! Тариф '{tariff['name']}' активирован.\n\nВы можете скачать конфигурационные файлы в личном кабинете.",
                    keyboard=Keyboards.back_keyboard("profile")
                )
            else:
                await self.send_message_and_save_id(
                    update=update,
                    context=context,
                    text="Ошибка активации тарифа. Пожалуйста, обратитесь в поддержку.",
                    keyboard=Keyboards.back_keyboard("profile")
                )
        else:
            await self.send_message_and_save_id(
                update=update,
                context=context,
                text=f"Статус платежа: {payment['status']}",
                keyboard=Keyboards.check_payment_keyboard(payment_id)
            )
        
        await self.db_manager.update_user_activity(user.id)

    async def generate_config_files(self, user_id: int, tariff: Dict[str, Any]) -> None:
        """Генерация конфигурационных файлов VPN"""
        # OpenVPN конфигурация
        openvpn_config = {
            "server": "vpn.earthvpn.com",
            "port": 1194,
            "protocol": "udp",
            "cipher": "AES-256-GCM",
            "username": f"user_{user_id}",
            "password": f"pass_{user_id}_{datetime.datetime.now().timestamp()}"
        }
        
        # WireGuard конфигурация
        wireguard_config = {
            "private_key": "abcdef1234567890",  # В реальном проекте - генерация ключей
            "public_key": "1234567890abcdef",
            "endpoint": "wg.earthvpn.com:51820",
            "allowed_ips": "0.0.0.0/0, ::/0",
            "dns": "1.1.1.1, 8.8.8.8"
        }
        
        # Сохраняем конфигурации в базу данных
        await self.db_manager.save_config(user_id, "openvpn", openvpn_config)
        await self.db_manager.save_config(user_id, "wireguard", wireguard_config)

    async def configs(self, update: Update, context: CallbackContext) -> None:
        """Обработчик запроса конфигурационных файлов"""
        user = update.effective_user
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text="Выберите тип конфигурации для скачивания:",
            keyboard=Keyboards.configs_keyboard()
        )
        
        await self.db_manager.update_user_activity(user.id)

    async def download_config(self, update: Update, context: CallbackContext) -> None:
        """Обработчик скачивания конфигурационного файла"""
        query = update.callback_query
        config_type = query.data.split('_')[1]
        user = update.effective_user
        
        # Получаем конфигурационные файлы пользователя
        configs = await self.db_manager.get_configs(user.id)
        
        # Находим нужную конфигурацию
        config = next((c for c in configs if c["config_type"] == config_type), None)
        
        if config:
            # Формируем текст конфигурационного файла
            if config_type == "openvpn":
                config_text = self.format_openvpn_config(config["config_data"])
            elif config_type == "wireguard":
                config_text = self.format_wireguard_config(config["config_data"])
            else:
                config_text = "Неподдерживаемый тип конфигурации"
            
            # Отправляем файл пользователю
            await context.bot.send_document(
                chat_id=user.id,
                document=config_text.encode(),
                filename=f"earthvpn_{config_type}.conf",
                caption=f"Конфигурация {config_type.upper()} для EarthVPN"
            )
            
            await self.send_message_and_save_id(
                update=update,
                context=context,
                text=f"✅ Конфигурационный файл {config_type.upper()} отправлен!",
                keyboard=Keyboards.configs_keyboard()
            )
        else:
            await self.send_message_and_save_id(
                update=update,
                context=context,
                text="Конфигурационный файл не найден. Пожалуйста, обратитесь в поддержку.",
                keyboard=Keyboards.back_keyboard("profile")
            )
        
        await self.db_manager.update_user_activity(user.id)

    def format_openvpn_config(self, config_data: Dict[str, Any]) -> str:
        """Форматирование конфигурационного файла OpenVPN"""
        return f"""client
dev tun
proto {config_data.get('protocol', 'udp')}
remote {config_data.get('server', 'vpn.earthvpn.com')} {config_data.get('port', 1194)}
resolv-retry infinite
nobind
persist-key
persist-tun
cipher {config_data.get('cipher', 'AES-256-GCM')}
auth SHA256
verb 3

<auth-user-pass>
{config_data.get('username', 'user')}
{config_data.get('password', 'pass')}
</auth-user-pass>
"""

    def format_wireguard_config(self, config_data: Dict[str, Any]) -> str:
        """Форматирование конфигурационного файла WireGuard"""
        return f"""[Interface]
PrivateKey = {config_data.get('private_key', '')}
Address = 10.0.0.2/24
DNS = {config_data.get('dns', '1.1.1.1, 8.8.8.8')}

[Peer]
PublicKey = {config_data.get('public_key', '')}
Endpoint = {config_data.get('endpoint', 'wg.earthvpn.com:51820')}
AllowedIPs = {config_data.get('allowed_ips', '0.0.0.0/0, ::/0')}
PersistentKeepalive = 25
"""

    async def payment_history(self, update: Update, context: CallbackContext) -> None:
        """Обработчик истории платежей"""
        user = update.effective_user
        
        # Получаем все платежи пользователя
        payments = await self.db_manager.get_user_payments(user.id)
        
        if payments:
            # Формируем текст с историей платежей
            text = "<b>История платежей:</b>\n\n"
            
            for payment in payments:
                tariff = next((t for t in TARIFFS if t["id"] == payment["tariff_id"]), None)
                tariff_name = tariff["name"] if tariff else "Неизвестный тариф"
                
                date = datetime.datetime.strptime(payment["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
                
                text += f"📅 <b>{date}</b>\n"
                text += f"🏷 Тариф: {tariff_name}\n"
                text += f"💰 Сумма: {payment['amount']} руб.\n"
                text += f"💳 Способ: {payment['payment_method']}\n"
                text += f"✅ Статус: {payment['status']}\n\n"
        else:
            text = "У вас пока нет истории платежей"
        
        await self.send_message_and_save_id(
            update=update,
            context=context,
            text=text,
            keyboard=Keyboards.payment_history_keyboard()
        )
        
        await self.db_manager.update_user_activity(user.id) 