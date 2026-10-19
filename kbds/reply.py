from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


del_kbd = ReplyKeyboardRemove()

start_kb = ReplyKeyboardBuilder()
start_kb.add(
    KeyboardButton(text='Справка'),
    KeyboardButton(text='Список ОЛТов'),
)
start_kb.adjust(2, 2)