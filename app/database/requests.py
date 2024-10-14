from app.database.models import async_session
from app.database.models import User, Category, Transaction
from sqlalchemy import select, update, delete

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_income_categories(user_id):
    async with async_session() as session:
        return await session.scalars(select(Category).where(Category.user_id == user_id, Category.type == 'income'))
    
async def get_expense_categories(user_id):
    async with async_session() as session:
        return await session.scalars(select(Category).where(Category.user_id == user_id, Category.type == 'expense'))
    
async def add_income(category: int, amount: float, description: str, tg_id:int, timestamp = str):
    async with async_session() as session:
        transaction = Transaction(type='income', amount=amount, description=description, user_id=tg_id, category = category, timestamp=timestamp)
        session.add(transaction)
        await session.commit()

async def add_expense(category: int, amount: float, description: str, tg_id:int, timestamp = str):
    async with async_session() as session:
        transaction = Transaction(type='expense', amount=amount, description=description, user_id=tg_id, category = category, timestamp=timestamp)
        session.add(transaction)
        await session.commit()

async def add_income_category(name: str, tg_id:int):
    async with async_session() as session:
        category = Category(type = 'income',name=name, user_id=tg_id)
        session.add(category)
        await session.commit()

async def add_expense_category(name: str, tg_id:int):
    async with async_session() as session:
        category = Category(type = 'expense',name=name, user_id=tg_id)
        session.add(category)
        await session.commit()

async def get_category_by_id(id: int):
    async with async_session() as session:
        return await session.scalar(select(Category.name).where(Category.id == id))
    
async def get_expense_transactions_by_category(id: int, tg_id:int):
    async with async_session() as session:
        return await session.scalars(select(Transaction.amount).where(Transaction.type == 'expense', Transaction.category == id, Transaction.user_id == tg_id))
    
async def get_income_transactions_by_category(id: int, tg_id:int):
    async with async_session() as session:
        return await session.scalars(select(Transaction.amount).where(Transaction.type == 'income', Transaction.category == id, Transaction.user_id == tg_id))
    
async def get_total_income(tg_id:int):
    async with async_session() as session:
        return await session.scalars(select(Transaction.amount).where(Transaction.type == 'income', Transaction.user_id == tg_id))
    
async def get_total_expense(tg_id:int):
    async with async_session() as session:
        return await session.scalars(select(Transaction.amount).where(Transaction.type == 'expense', Transaction.user_id == tg_id))    

async def update_category_name(id: int, tg_id: int, new_name: str):
    async with async_session() as session:
        stmt = (
            update(Category)
            .where(Category.id == id, Category.user_id == tg_id)
            .values(name=new_name)
        )
        await session.execute(stmt)
        await session.commit()

async def delete_category(id: int, tg_id: int):
    async with async_session() as session:
        stmt = (
            delete(Category)
            .where(Category.id == id, Category.user_id == tg_id)
        )
        await session.execute(stmt)
        await session.commit()

async def delete_transactions_by_category(id: int, tg_id: int):
    async with async_session() as session:
        stmt = (
            delete(Transaction)
            .where(Transaction.category == id, Transaction.user_id == tg_id)
        )
        await session.execute(stmt)
        await session.commit()

async def update_transaction_amount(id: int, tg_id: int, new_amount: int):
    async with async_session() as session:
        stmt = (
            update(Transaction)
            .where(Transaction.category == id, Transaction.user_id == tg_id)
            .values(amount=new_amount)
        )
        await session.execute(stmt)
        await session.commit()