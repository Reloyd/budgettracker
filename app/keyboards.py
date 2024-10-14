from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.models import User
from datetime import datetime

import logging

from app.database.requests import get_expense_categories, get_income_categories

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить категории')],
    [KeyboardButton(text='Добавить доход'),
      KeyboardButton(text='Добавить расход')],
    [KeyboardButton(text='Ваши доходы')],
    [KeyboardButton(text='Ваши расходы по категориям')]
], resize_keyboard=True)

manage_expense_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить название категории', callback_data='edit_expense_name')],
    [InlineKeyboardButton(text='Изменить сумму трат по категории', callback_data='edit_expense_amount')],
    [InlineKeyboardButton(text='Удалить категорию', callback_data='delete_expense_category')],
    [InlineKeyboardButton(text='Вернуться назад', callback_data='expense_back')]
])

manage_income_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить название категории', callback_data='edit_income_name')],
    [InlineKeyboardButton(text='Изменить сумму поступлений по категории', callback_data='edit_income_amount')],
    [InlineKeyboardButton(text='Удалить категорию', callback_data='delete_income_category')],
    [InlineKeyboardButton(text='Вернуться назад', callback_data='income_back')]
])

add_categories = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Доход', callback_data='add_category_income')],
    [InlineKeyboardButton(text='Расход', callback_data='add_category_expense')],
])

async def stat_income_categories(user_id):
    all_categories = await get_income_categories(user_id)
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"income_stat_category_{category.id}"))
    return keyboard.adjust(1).as_markup()

async def stat_expense_categories(user_id):
    all_categories = await get_expense_categories(user_id)
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"expense_stat_category_{category.id}"))
    return keyboard.adjust(1).as_markup()

## клавиатура с категориями расходов
async def expense_categories(user_id):
    all_categories = await get_expense_categories(user_id)
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"expense_category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='Добавить категорию', callback_data='new_expense_category'))
    return keyboard.adjust(1).as_markup()

## клавиатура с категориями доходов
async def income_categories(user_id):
    all_categories = await get_income_categories(user_id)
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"income_category_{category.id}"))
    keyboard.add(InlineKeyboardButton(text='Добавить категорию', callback_data='new_income_category'))
    return keyboard.adjust(1).as_markup()

    