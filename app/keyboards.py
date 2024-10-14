from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.models import User

from app.database.requests import get_categories

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить категорию расходов')],
    [KeyboardButton(text='Добавить доход'),
      KeyboardButton(text='Добавить расход')],
    [KeyboardButton(text='Ваши доходы')],
    [KeyboardButton(text='Ваши расходы по категориям')]
], resize_keyboard=True)

async def categories(user_id):
    all_categories = await get_categories(user_id)
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"stat_category_{category.id}"))
    return keyboard.adjust(1).as_markup()

async def expense_categories(user_id):
    all_categories = await get_categories(user_id)
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='Добавить категорию', callback_data='new_category'))
    return keyboard.adjust(1).as_markup()