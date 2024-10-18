from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime

import app.keyboards as kb
import app.database.requests as rq

router = Router()

class AddIncome(StatesGroup):
    category = State()
    amount = State()
    description = State()

class AddExpense(StatesGroup):
    category = State()
    amount = State()
    description = State()

class AddExpenseCategory(StatesGroup):
    name = State()

class AddIncomeCategory(StatesGroup):
    name = State()

class AddReplyExpenseCategory(StatesGroup):
    name = State()

class AddReplyIncomeCategory(StatesGroup):
    name = State() 

class ManageExpenseCategory(StatesGroup):
    category_id = State()
    transaction_id = State()
    new_name = State()
    new_amount = State()

class ManageIncomeCategory(StatesGroup):
    category_id = State()
    new_name = State()
    new_amount = State()

class TotalExpense(StatesGroup):
    total_expense = State()

async def count_total_expnese(user_id: int):
    transactions = await rq.get_total_expense(user_id)
    total_expense = 0
    for transaction in transactions:
        total_expense += transaction
    return total_expense

async def count_total_income(user_id: int):
    incomes = await rq.get_total_income(user_id)
    total_incomes = 0
    for income in incomes:
        total_incomes += income
    return total_incomes

async def count_category_expense(category_id: int, user_id: int):
    transactions = await rq.get_expense_transactions_by_category(category_id, user_id)
    total_amount = 0
    for transaction in transactions:
        total_amount += transaction
    return total_amount 

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Привет! Я - бот для управления личными финансами.\n\n'
                          'Вот краткое руководство по использованию:\n\n'
                          '1. Выберите действие:\n'
                          '   - Добавить доход или расход\n'
                          '   - Просмотреть доходы или расходы\n'
                          '   - Добавить категорию\n\n'
                          '2. Для добавления дохода/расхода:\n'
                          '   - Выберите категорию\n'
                          '   - Если необходимой категории нет - создайте её\n'
                          '   - Введите сумму в рублях\n'
                          '   - Опишите транзакцию\n\n'
                          '3. Для просмотра статистики:\n'
                          '   - Выберите категорию для детального просмотра\n'
                          '   - Просмотрите общие доходы/расходы по всем категориям\n\n'
                          '4. Для управления категориями:\n'
                          '   - Добавьте новую категорию\n'
                          '   - Измените название или сумму существующей категории\n'
                          '   - Удалите ненужную категорию\n\n'
                          'Помните, что вы можете возвращаться на предыдущий экран с помощью кнопки "Вернуться".\n\n'
                          'Если у вас есть вопросы, не стесняйтесь обращаться к администратору бота.', reply_markup=kb.main)

@router.message(F.text == 'Ваши расходы по категориям')
async def categories(message: Message, state:FSMContext):
    total_expense = await count_total_expnese(message.from_user.id)
    await state.set_state(ManageExpenseCategory.category_id)
    await message.answer(f'Ваши общие траты по всем категория составили: {total_expense}₽\n' +
                          'Выберите категорию, чтоб узнать траты по ней:',
                            reply_markup=await kb.stat_expense_categories(message.from_user.id))

@router.message(F.text == 'Добавить расход')
async def add_expense(message: Message):
    await message.reply("Выберите категорию расхода:", reply_markup=await kb.expense_categories(message.from_user.id))


@router.callback_query(F.data == 'new_expense_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы добавляете новую категорию')
    await state.set_state(AddExpenseCategory.name)
    await callback.message.edit_text('Введите название категории:')

@router.message(AddExpenseCategory.name)
async def add_category_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await rq.add_expense_category(data['name'], message.from_user.id)
    await message.answer('Выберите категорию расхода:', reply_markup=await kb.expense_categories(message.from_user.id))
    await state.clear()

@router.callback_query(F.data.startswith('expense_category_'))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
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

@router.message(F.text == 'Добавить доход')
async def add_income(message: Message):
    await message.reply("Выберите категорию дохода:", reply_markup=await kb.income_categories(message.from_user.id))


@router.callback_query(F.data == 'new_income_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы добавляете новую категорию')
    await state.set_state(AddIncomeCategory.name)
    await callback.message.edit_text('Введите название категории:')

@router.message(AddIncomeCategory.name)
async def add_category_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await rq.add_income_category(data['name'], message.from_user.id)
    await message.answer('Выберите категорию дохода:', reply_markup=await kb.income_categories(message.from_user.id))
    await state.clear()

@router.callback_query(F.data.startswith('income_category_'))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(category = category_id)
    await callback.answer()
    category_name = await rq.get_category_by_id(category_id)
    await state.set_state(AddIncome.amount)
    await callback.message.edit_text(f"Вы выбрали категорию: {category_name}. Введите сумму дохода в рублях: ")

@router.message(AddIncome.amount)
async def add_expense_amount(message: Message, state: FSMContext):
    user = message.from_user
    current_time = datetime.now()
    await state.update_data(
        tg_id=user.id,
        timestamp=current_time
    )
    await state.update_data(amount = message.text)
    await state.set_state(AddIncome.description)
    await message.answer('Введите описание дохода:')

@router.message(AddIncome.description)
async def add_income_description(message: Message, state: FSMContext):
    await state.update_data(description = message.text)
    data = await state.get_data()
    await rq.add_income(data['category'], data['amount'], data['description'], data['tg_id'], data['timestamp'])
    await message.answer('Доход успешно добавлен!', reply_markup=kb.main)
    await state.clear()

@router.message(ManageExpenseCategory.category_id)
@router.callback_query(F.data.startswith('expense_stat_category_'))
async def stat_category_selected(callback: CallbackQuery, state:FSMContext):
    category_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=category_id)
    total_expense = await count_category_expense(category_id, callback.from_user.id)
    await state.set_state(ManageExpenseCategory.transaction_id)    
    await callback.message.edit_text(f"Общая сумма трат по этой категории составляет: {total_expense}₽", reply_markup = await kb.expense_transactions(category_id, callback.from_user.id))

@router.message(ManageExpenseCategory.transaction_id)
@router.callback_query(F.data.startswith('expense_transaction_'))
async def expense_transaction_selected(callback: CallbackQuery, state:FSMContext):
    transaction_id = int(callback.data.split("_")[2])
    await state.update_data(transaction_id = transaction_id)
    await callback.message.edit_text(f"Выберите что сделать:", reply_markup=kb.manage_expense_transaction)

@router.callback_query(F.data.startswith('income_stat_category_'))
async def stat_category_selected(callback: CallbackQuery, state:FSMContext):
    category_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=category_id)
    transactions = await rq.get_income_transactions_by_category(category_id, callback.from_user.id)
    total_amount = 0
    for transaction in transactions:
        total_amount += transaction    
    await callback.message.edit_text(f"Общая сумма доходов по этой категории составляет: {total_amount}₽", reply_markup = kb.manage_income_categories)

@router.message(F.text == 'Ваши доходы по категориям')
async def show_incomes(message: Message):
    total_incomes = await count_total_income(message.from_user.id)
    await message.answer(f'Ваши общие доходы по всем категория составили: {total_incomes}₽\n' +
                          'Выберите категорию, чтоб узнать доходы по ней:',
                            reply_markup=await kb.stat_income_categories(message.from_user.id))
    

@router.message(F.text == 'Добавить категории')
async def add_reply_category(message: Message, state: FSMContext):
    await message.answer('Какую категорию вы хотите создать?', reply_markup= kb.add_categories)

@router.callback_query(F.data == 'add_category_income')
async def add_category_income(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddReplyIncomeCategory.name)
    await callback.message.reply('Введите название категории:')
    await callback.answer('')

@router.message(AddReplyIncomeCategory.name)
async def add_reply_income_category_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await rq.add_income_category(data['name'], message.from_user.id)
    await message.answer('Категория успешно создана!', reply_markup=kb.main)
    await state.clear()


@router.callback_query(F.data == 'add_category_expense')
async def add_category_expense(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddReplyExpenseCategory.name)
    await callback.message.reply('Введите название категории:')

@router.message(AddReplyExpenseCategory.name)
async def add_reply_expense_category_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    data = await state.get_data()
    await rq.add_expense_category(data['name'], message.from_user.id)
    await message.answer('Категория успешно создана!', reply_markup=kb.main)
    await state.clear()

@router.callback_query(F.data == 'expense_back')
async def back_to_expense_categories(callback: CallbackQuery, state:FSMContext):
    user_data = await state.get_data()
    await callback.message.delete()
    total_expense = await count_category_expense(user_data['category_id'], callback.from_user.id)
    await callback.message.answer(f'Ваши общие траты по всем категория составили: {total_expense}₽\n' +
                                    'Выберите категорию, чтоб узнать траты по ней:',
                                    reply_markup = await kb.expense_transactions(user_data['category_id'], callback.from_user.id))
    await state.clear()
    
@router.callback_query(F.data == 'back_to_expense_categories')
async def back_to_expense_categories(callback: CallbackQuery, state:FSMContext):
    await callback.message.delete()
    total_expense = await count_total_expnese(callback.from_user.id)
    await callback.message.answer(f'Ваши общие траты по всем категория составили: {total_expense}₽\n' +
                                    'Выберите категорию, чтоб узнать траты по ней:',
                                    reply_markup = await kb.stat_expense_categories(callback.from_user.id))
    await state.clear()

@router.callback_query(F.data == 'edit_expense_transaction_name')
async def edit_name_expense_transaction(callback: CallbackQuery, state:FSMContext):
    await state.set_state(ManageExpenseCategory.new_name)
    await callback.message.reply('Введите новое описание транзакции:')
    await callback.answer()

@router.message(ManageExpenseCategory.new_name)
async def edit_name_expense_category_final(message: Message, state: FSMContext):
    await state.update_data(new_name = message.text)
    user_data = await state.get_data()
    await rq.update_category_name(user_data['transaction_id'], user_data['category_id'], message.from_user.id, user_data['new_name'])
    total_expense = await count_total_expnese(message.from_user.id)
    await message.answer(f'Ваши общие траты по всем категория составили: {total_expense}₽\n' +
                                    'Выберите категорию, чтоб узнать траты по ней:',
                                    reply_markup = await kb.stat_expense_categories(message.from_user.id))
    await state.clear()

@router.message(ManageExpenseCategory.category_id)
@router.callback_query(F.data == 'delete_expense_transaction')
async def delete_expense_category(callback: CallbackQuery, state:FSMContext):
    user_data = await state.get_data()
    await rq.delete_transaction_by_id(user_data['transaction_id'], user_data['category_id'], callback.from_user.id)
    total_expense = await count_total_expnese(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(f'Ваши общие траты по всем категория составили: {total_expense}₽\n' +
                                    'Выберите категорию, чтоб узнать траты по ней:',
                                    reply_markup = await kb.stat_expense_categories(callback.from_user.id))
    await state.clear()

@router.callback_query(F.data == 'edit_expense_amount')
async def edit_expense_amount(callback: CallbackQuery, state:FSMContext):
    await state.set_state(ManageExpenseCategory.new_amount)
    await callback.message.reply('Введите новую сумму:')
    await callback.answer()

@router.message(ManageExpenseCategory.new_amount)
async def edit_expense_amount_final(message: Message, state: FSMContext):
    await state.update_data(new_amount = message.text)
    user_data = await state.get_data()
    await rq.update_transaction_amount(user_data['transaction_id'], user_data['category_id'],message.from_user.id, user_data['new_amount'])
    total_expense = await count_total_expnese(message.from_user.id)
    await message.answer(f'Ваши общие траты по всем категория составили: {total_expense}₽\n' +
                                    'Выберите категорию, чтоб узнать траты по ней:',
                                    reply_markup = await kb.stat_expense_categories(message.from_user.id))
    await state.clear()

@router.callback_query(F.data == 'income_back')
async def back_to_income_categories(callback: CallbackQuery, state:FSMContext):
    await callback.message.delete()
    total_income = await count_total_income(callback.from_user.id)
    await callback.message.answer(f'Ваши общие доходы по всем категория составили: {total_income}₽\n' +
                                    'Выберите категорию, чтоб узнать доходы по ней:',
                                    reply_markup = await kb.stat_income_categories(callback.from_user.id))

@router.callback_query(F.data == 'edit_income_name')
async def edit_name_income_category(callback: CallbackQuery, state:FSMContext):
    await state.set_state(ManageIncomeCategory.new_name)
    await callback.message.reply('Введите новое название категории:')
    await callback.answer()

@router.message(ManageIncomeCategory.new_name)
async def edit_name_income_category_final(message: Message, state: FSMContext):
    await state.update_data(new_name = message.text)
    user_data = await state.get_data()
    await rq.update_category_name(user_data['category_id'], message.from_user.id, user_data['new_name'])
    total_income = await count_total_income(message.from_user.id)
    await message.answer(f'Ваши общие доходы по всем категория составили: {total_income}₽\n' +
                                    'Выберите категорию, чтоб узнать доходы по ней:',
                                    reply_markup = await kb.stat_income_categories(message.from_user.id))

@router.callback_query(F.data == 'delete_income_category')
async def delete_income_category(callback: CallbackQuery, state:FSMContext):
    user_data = await state.get_data()
    await rq.delete_category(user_data['category_id'], callback.from_user.id)
    await rq.delete_transactions_by_category(user_data['category_id'], callback.from_user.id)
    total_income = await count_total_income(callback.from_user.id)
    await callback.message.delete()
    await callback.message.answer(f'Ваши общие доходы по всем категория составили: {total_income}₽\n' +
                                    'Выберите категорию, чтоб узнать доходы по ней:',
                                    reply_markup = await kb.stat_income_categories(callback.from_user.id))
    
@router.callback_query(F.data == 'edit_income_amount')
async def edit_income_amount(callback: CallbackQuery, state:FSMContext):
    await state.set_state(ManageIncomeCategory.new_amount)
    await callback.answer()
    await callback.message.reply('Введите новую сумму:')

@router.message(ManageIncomeCategory.new_amount)
async def edit_amount_income_final(message: Message, state: FSMContext):
    await state.update_data(new_amount = message.text)
    user_data = await state.get_data()
    await rq.update_transaction_amount(user_data['category_id'],message.from_user.id, user_data['new_amount'])
    total_income = await count_total_income(message.from_user.id)
    await message.answer(f'Ваши общие доходы по всем категория составили: {total_income}₽\n' +
                                    'Выберите категорию, чтоб узнать доходы по ней:',
                                    reply_markup = await kb.stat_income_categories(message.from_user.id))