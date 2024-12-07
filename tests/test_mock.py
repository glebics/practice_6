# tests/test_mock.py

import pytest
from app import schemas


@pytest.mark.asyncio
async def test_get_dynamics_mocked(crud_mock, client):
    # Настройка мок-функции с использованием mocker
    mock_trading_results = [
        schemas.TradingResult(
            exchange_product_id="A592VLA060F",
            exchange_product_name="Бензин (АИ-92-К5) по ГОСТ, ст. Ветласян (ст. отправления)",
            oil_id="A592",
            delivery_basis_id="ст. Ветласян",
            delivery_basis_name="",
            delivery_type_id="58428",
            volume=360.0,
            total=21227700.0,
            count=6,
            date="2024-11-27T00:00:00",
            pk_spimex_id=69,
            created_on="2024-11-27T15:39:28.633005",
            updated_on="2024-11-27T15:39:28.633005"
        )
    ]
    # Убедитесь, что правильно мокируете функцию
    crud_mock.return_value = mock_trading_results

    # Отправка запроса к эндпоинту
    response = await client.get("/get_dynamics?oil_id=A592")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["exchange_product_id"] == "A592VLA060F"