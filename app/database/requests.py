from app.database.models import async_session
from app.database.models import User, Category, Transaction
from sqlalchemy import select

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_categories(user_id):
    async with async_session() as session:
        return await session.scalars(select(Category).where(Category.user_id == user_id))
    
async def add_income(amount: float, description: str, tg_id:int, timestamp = str):
    async with async_session() as session:
        transaction = Transaction(type='income', amount=amount, description=description, user_id=tg_id, category='income', timestamp = timestamp)
        session.add(transaction)
        await session.commit()

async def add_expense(category: int, amount: float, description: str, tg_id:int, timestamp = str):
    async with async_session() as session:
        transaction = Transaction(type='expense', amount=amount, description=description, user_id=tg_id, category = category, timestamp=timestamp)
        session.add(transaction)
        await session.commit()

async def add_category(name: str, tg_id:int):
    async with async_session() as session:
        category = Category(name=name, user_id=tg_id)
        session.add(category)
        await session.commit()

async def get_category_by_id(id: int):
    async with async_session() as session:
        return await session.scalar(select(Category.name).where(Category.id == id))
    
async def get_transactions_by_category(id: int, tg_id:int):
    async with async_session() as session:
        return await session.scalars(select(Transaction.amount).where(Transaction.type == 'expense', Transaction.category == id, Transaction.user_id == tg_id))
    
async def get_income_transaction(tg_id:int):
    async with async_session() as session:
        return await session.scalars(select(Transaction.amount).where(Transaction.type == 'income', Transaction.user_id == tg_id))
    
async def get_total_expense(tg_id:int):
    async with async_session() as session:
        return await session.scalars(select(Transaction.amount).where(Transaction.type == 'expense', Transaction.user_id == tg_id))