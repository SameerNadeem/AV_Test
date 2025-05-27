from src.api.bottler import create_bottle_plan


def test_bottle_red_potions() -> None:
    # changed the inventory to 500ml of liquid enough for 5 red potions
    red_ml: int = 500
    green_ml: int = 0
    blue_ml: int = 0
    dark_ml: int = 0
    maximum_potion_capacity: int = 1000
    current_potion_count: int = 0

    # include price as the 5th element
    potion_catalog = [(100, 0, 0, 0, 1)]  # 100ml red potion 1 gold each

    result = create_bottle_plan(
        red_ml=red_ml,
        green_ml=green_ml,
        blue_ml=blue_ml,
        dark_ml=dark_ml,
        maximum_potion_capacity=maximum_potion_capacity,
        current_potion_count=current_potion_count,
        potion_catalog=potion_catalog,
    )

    assert len(result) == 1
    assert result[0].potion_type == [100, 0, 0, 0]
    assert result[0].quantity == 5
