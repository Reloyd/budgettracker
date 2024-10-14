from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime

import app.keyboards as kb
from app.middlewares import TestMiddleWare
import app.database.requests as rq
import logging

router = Router()

router.message.outer_middleware(TestMiddleWare())

class AddIncome(StatesGroup):
    amount = State()
    description = State()

class AddExpense(StatesGroup):
    category = State()
    amount = State()
    description = State()

class AddCategory(StatesGroup):
    name = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.reply('Привет!', reply_markup=kb.main)

@router.message(F.text == 'Ваши расходы по категориям')
async def categories(message: Message):
    transactions = await rq.get_total_expense(message.from_user.id)
    total_expense = 0
    for transaction in transactions:
        total_expense += transaction
    await message.answer(f'Ваши общие траты по всем категория составили: {total_expense}₽\n' +
                          'Выберите категорию, чтоб узнать траты по ней:',
                            reply_markup=await kb.categories(message.from_user.id))

@router.message(F.text == 'Добавить доход')
async def add_income_amount(message: Message, state: FSMContext):
    user = message.from_user
    current_time = datetime.now()
    await state.update_data(
        tg_id=user.id,
        timestamp=current_time
    )
    await state.set_state(AddIncome.amount)
    await message.answer('Введите сумму дохода')

@router.message(AddIncome.amount)
async def add_income_description(message: Message, state: FSMContext):
    await state.update_data(amount = message.text)
    await state.set_state(AddIncome.description)
    await message.answer('Введите описание дохода')

@router.message(AddIncome.description)
async def add_income_description(message: Message, state: FSMContext):
    await state.update_data(description = message.text)
    data = await state.get_data()
    await rq.add_income(data['amount'], data['description'], data['tg_id'], data['timestamp'])
    await message.answer('Доход успешно добавлен!', reply_markup=kb.main)
    await state.clear()

@router.message(F.text == 'Добавить расход')
async def add_expense(message: Message):
    await message.reply("Выберите категорию расхода:", reply_markup=await kb.expense_categories(message.from_user.id))


@router.callback_query(F.data == 'new_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы добавляете новую категорию')
    await state.set_state(AddCategory.name)
    await callback.message.edit_text('Введите название категории:')

@router.message(AddCategory.name)
async def add_category_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await rq.add_category(data['name'], message.from_user.id)
    await message.answer('Выберите категорию расхода:', reply_markup=await kb.expense_categories(message.from_user.id))
    await state.clear()

@router.callback_query(F.data.startswith('category_'))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category = category_id)
    await callback.answer()
    category_name = await rq.get_category_by_id(category_id)
    await state.set_state(AddExpense.amount)
    await callback.message.edit_text(f"Вы выбрали категорию: {category_name}. Введите сумму расхода в рублях: ")

@router.message(AddExpense.amount)
async def add_expense_amount(message: Message, state: FSMContext):
    user = message.from_user
    current_time = datetime.now()
    await state.update_data(
        tg_id=user.id,
        timestamp=current_time
    )
    await state.update_data(amount = message.text)
    await state.set_state(AddExpense.description)
    await message.answer('Введите описание расхода:')

@router.message(AddExpense.description)
async def add_income_description(message: Message, state: FSMContext):
    await state.update_data(description = message.text)
    data = await state.get_data()
    await rq.add_expense(data['category'], data['amount'], data['description'], data['tg_id'], data['timestamp'])
    await message.answer('Расход успешно добавлен!', reply_markup=kb.main)
    await state.clear()

@router.callback_query(F.data.startswith('stat_category_'))
async def stat_category_selected(callback: CallbackQuery):
    category_id = int(callback.data.split("_")[2])
    transactions = await rq.get_transactions_by_category(category_id, callback.from_user.id)
    total_amount = 0
    for transaction in transactions:
        total_amount += transaction    
    await callback.message.reply(f"Общая сумма трат по этой категории составляет: {total_amount}₽")
    await callback.answer()

@router.message(F.text == 'Ваши доходы')
async def show_incomes(message: Message):
    incomes = await rq.get_income_transaction(message.from_user.id)
    total_incomes = 0
    for income in incomes:
        total_incomes += income
    await message.reply(f"Общая сумма ваших доходов составляет: {total_incomes}₽")