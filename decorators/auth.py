from functools import wraps
from aiogram import types

from services.logger import log_write
from services.backend_api_connect import post_api_auth
from variables.users import oltshub_tokens


def user_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # 1. Ищем объект message среди переданных позиционных аргументов
        message = next((arg for arg in args if isinstance(arg, types.Message)), None)
        
        # 2. Если в позиционных нет, ищем в именованных (на всякий случай)
        if not message:
            message = kwargs.get('message')
            
        # 3. Если message не найден вообще (функцию вызвали неправильно)
        if not message:
            raise ValueError("Декоратор user_required можно использовать только с хендлерами, принимающими Message")

        # 4. Проверяем ID пользователя
        if str(message.from_user.id) not in oltshub_tokens: #[str(message.from_user.id)]:
            await message.answer(f"У вас нет доступа к этой команде. ❌\nВойдите с помощью команды <code>/login ВАШ_ЛОГИН</code>\nВаш ID {message.from_user.id}")
            log_write(f'User: {message.from_user.id}; Action: AUTH; Message: Нет доступа. Text: {message.text}')

            return # Прерываем выполнение, функцию `f` не вызываем

        # Если всё ок, передаем управление исходной функции
        log_write(f'User: {message.from_user.id}; Action: AUTH; Message: {message.text}')

        return await f(*args, **kwargs)
        
    return decorated


def auth(login, telegram_id):
    '''
    Функция получения токена из OLTsHUB
    '''
    result = post_api_auth('/api/telegram/auth', {'login': login, 'telegram_id': telegram_id})

    return result
    
