# tests/test_crud.py

import pytest
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models


@pytest.mark.asyncio
async def test_get_last_trading_dates(db_session: AsyncSession) -> None:
    """
    Тестирует функцию `get_last_trading_dates` для проверки получения последних торговых дат.

    Создаёт 10 записей с разными датами и проверяет, что функция возвращает корректное количество последних дат.
    """
    # Подготовка данных
    now = datetime.utcnow()
    trading_dates = [
        models.SpimexTradingResultAsync(
            exchange_product_id=f"EP{i}",
            exchange_product_name=f"Product {i}",
            oil_id="A1",
            delivery_type_id="D1",
            delivery_basis_id="B1",
            delivery_basis_name="Basis",
            volume=100.0 + i,
            total=1000.0 + i * 100,
            count=10 + i,
            date=now - timedelta(days=i),
            created_on=now,
            updated_on=now
        )
        for i in range(10)
    ]
    db_session.add_all(trading_dates)
    await db_session.commit()

    # Тестирование функции
    result: List[datetime.date] = await crud.get_last_trading_dates(db_session, limit=5)
    assert len(result) == 5
    expected_dates: List[datetime.date] = [
        (now - timedelta(days=i)).date() for i in range(5)]
    assert result == expected_dates


@pytest.mark.asyncio
async def test_get_dynamics_no_filters(db_session: AsyncSession) -> None:
    """
    Тестирует функцию `get_dynamics` без применения фильтров.

    Создаёт 10 записей и проверяет, что функция возвращает все записи без фильтрации.
    """
    # Подготовка данных
    trading_results = [
        models.SpimexTradingResultAsync(
            exchange_product_id=f"EP{i}",
            exchange_product_name=f"Product {i}",
            oil_id="A1",
            delivery_type_id="D1",
            delivery_basis_id="B1",
            delivery_basis_name="Basis",
            volume=100.0 + i,
            total=1000.0 + i * 100,
            count=10 + i,
            date=datetime.utcnow(),
            created_on=datetime.utcnow(),
            updated_on=datetime.utcnow()
        )
        for i in range(10)
    ]
    db_session.add_all(trading_results)
    await db_session.commit()

    # Тестирование функции
    result: List[models.SpimexTradingResultAsync] = await crud.get_dynamics(db_session, None, None, None, None, None)
    assert len(result) == 10


@pytest.mark.asyncio
async def test_get_trading_results_with_filters(db_session: AsyncSession) -> None:
    """
    Тестирует функцию `get_trading_results` с применением фильтров.

    Создаёт 10 записей с разными значениями фильтров и проверяет, что функция возвращает корректное количество записей.
    """
    # Подготовка данных
    trading_results = [
        models.SpimexTradingResultAsync(
            exchange_product_id=f"EP{i}",
            exchange_product_name=f"Product {i}",
            oil_id="A1" if i % 2 == 0 else "A2",
            delivery_type_id="D1" if i % 3 == 0 else "D2",
            delivery_basis_id="B1",
            delivery_basis_name="Basis",
            volume=100.0 + i,
            total=1000.0 + i * 100,
            count=10 + i,
            date=datetime.utcnow(),
            created_on=datetime.utcnow(),
            updated_on=datetime.utcnow()
        )
        for i in range(10)
    ]
    db_session.add_all(trading_results)
    await db_session.commit()

    # Тестирование функции с фильтрами
    result: List[models.SpimexTradingResultAsync] = await crud.get_trading_results(
        db_session,
        oil_id="A1",
        delivery_type_id="D1",
        delivery_basis_id="B1",
        limit=5
    )
    expected_count: int = len([
        tr for tr in trading_results
        if tr.oil_id == "A1" and tr.delivery_type_id == "D1" and tr.delivery_basis_id == "B1"
    ])
    assert len(result) == expected_count
