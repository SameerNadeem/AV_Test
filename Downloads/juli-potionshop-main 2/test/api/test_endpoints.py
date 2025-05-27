import pytest
from fastapi.testclient import TestClient
from src.api.server import app
import sqlalchemy
from src import database as db

client = TestClient(app)
HEADERS = {"access_token": "brat"}


"""
Added auto skip for db-dependent test when data isnt available
created helper to check db connection
added pytest to skip test if data cant be reached
"""


def db_is_available():
    try:
        with db.engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.mark.skipif(not db_is_available(), reason="Skipping test: DB not available")
def test_admin_reset():
    response = client.post("/admin/reset", headers=HEADERS)
    assert response.status_code == 204


@pytest.mark.skipif(not db_is_available(), reason="Skipping test: DB not available")
def test_inventory_audit():
    response = client.get("/inventory/audit", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "ml_in_barrels" in data
    assert "number_of_potions" in data
    assert "gold" in data


@pytest.mark.skipif(not db_is_available(), reason="Skipping test: DB not available")
def test_catalog_endpoint():
    response = client.get("/catalog/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.skipif(not db_is_available(), reason="Skipping test: DB not available")
def test_cart_checkout_flow():
    # Reset state
    client.post("/admin/reset", headers=HEADERS)

    # Seed gold
    with db.engine.begin() as conn:
        conn.execute(
            sqlalchemy.text("""
            INSERT INTO gold_inventory (gold) VALUES (500)
            ON CONFLICT (id) DO UPDATE SET gold = EXCLUDED.gold
        """)
        )
        conn.execute(
            sqlalchemy.text("""
            INSERT INTO potion_catalog (sku, name, price, r, g, b, d)
            VALUES ('TEST_POTION', 'Test Potion', 50, 100, 0, 0, 0)
            ON CONFLICT (sku) DO UPDATE SET price = 50
        """)
        )
        conn.execute(
            sqlalchemy.text("""
            INSERT INTO potion_inventory (sku, quantity)
            VALUES ('TEST_POTION', 5)
            ON CONFLICT (sku) DO UPDATE SET quantity = 5
        """)
        )

    # Create cart
    new_cart = {
        "customer_id": "brat1",
        "customer_name": "brat",
        "character_class": "mage",
        "level": 10,
    }
    response = client.post("/carts/", json=new_cart, headers=HEADERS)
    assert response.status_code == 200
    cart_id = response.json()["cart_id"]

    # Add item to cart
    response = client.post(
        f"/carts/{cart_id}/items/TEST_POTION",
        json={"quantity": 1},
        headers=HEADERS,
    )
    assert response.status_code == 204

    # Checkout
    response = client.post(
        f"/carts/{cart_id}/checkout",
        json={"payment": "gold"},
        headers=HEADERS,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["total_potions_bought"] == 1
    assert result["total_gold_paid"] == 50

    # Confirm gold deduction
    audit = client.get("/inventory/audit", headers=HEADERS).json()
    assert audit["gold"] == 450


@pytest.mark.skipif(not db_is_available(), reason="DB not available")
def test_deliver_barrel():
    order_id = "11111111-1111-1111-1111-111111111111"  # UUID format
    barrel = [
        {
            "sku": "B001",
            "ml_per_barrel": 1000,
            "potion_type": [1.0, 0.0, 0.0, 0.0],
            "price": 25,
            "quantity": 1,
        }
    ]
    response = client.post(f"/barrels/deliver/{order_id}", json=barrel, headers=HEADERS)
    assert response.status_code in [204, 400]


@pytest.mark.skipif(not db_is_available(), reason="DB not available")
def test_bottle_plan():
    response = client.post("/bottler/plan", json=[], headers=HEADERS)
    assert response.status_code == 200
    plan = response.json()
    assert isinstance(plan, list)
    for potion in plan:
        assert sum(potion["potion_type"]) == 100


@pytest.mark.skipif(not db_is_available(), reason="DB not available")
def test_deliver_potions():
    order_id = "22222222-2222-2222-2222-222222222222"
    potions = [{"potion_type": [100, 0, 0, 0], "quantity": 1}]
    response = client.post(
        f"/bottler/deliver/{order_id}", json=potions, headers=HEADERS
    )
    assert response.status_code in [204, 400]


@pytest.mark.skipif(not db_is_available(), reason="DB not available")
def test_inventory_values_after_delivery():
    response = client.get("/inventory/audit", headers=HEADERS)
    assert response.status_code == 200
    audit = response.json()
    assert isinstance(audit["ml_in_barrels"], int)
    assert isinstance(audit["gold"], int)
    assert isinstance(audit["number_of_potions"], int)
