# tests/test_endpoints.py

import pytest
from datetime import datetime, timedelta
from app import models


@pytest.mark.asyncio
async def test_get_last_trading_dates(client, db_session):
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
            date=(now - timedelta(days=i)).date(),
            created_on=now,
            updated_on=now
        )
        for i in range(5)
    ]
    db_session.add_all(trading_dates)
    await db_session.commit()

    # Отправка запроса к эндпоинту
    response = await client.get("/get_last_trading_dates?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    expected_dates = [(now - timedelta(days=i)).date().isoformat()
                      for i in range(3)]
    assert data == expected_dates


@pytest.mark.asyncio
async def test_get_dynamics(client, db_session):
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
            date=datetime.utcnow() - timedelta(days=i),
            pk_spimex_id=i,  # Убедитесь, что pk_spimex_id автогенерируется
            created_on=datetime.utcnow(),
            updated_on=datetime.utcnow()
        )
        for i in range(5)
    ]
    db_session.add_all(trading_results)
    await db_session.commit()

    # Отправка запроса к эндпоинту с фильтрами
    response = await client.get("/get_dynamics?oil_id=A1&delivery_type_id=D1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    for item in data:
        assert item["oil_id"] == "A1"
        assert item["delivery_type_id"] == "D1"


@pytest.mark.asyncio
async def test_get_trading_results(client, db_session):
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
            date=datetime.utcnow() - timedelta(days=i),
            pk_spimex_id=i,  # Убедитесь, что pk_spimex_id автогенерируется
            created_on=datetime.utcnow(),
            updated_on=datetime.utcnow()
        )
        for i in range(10)
    ]
    db_session.add_all(trading_results)
    await db_session.commit()

    # Отправка запроса к эндпоинту с фильтрами и лимитом
    response = await client.get("/get_trading_results?oil_id=A1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    for item in data:
        assert item["oil_id"] == "A1"
