from aiogram.fsm.state import State, StatesGroup

class RecipeStates(StatesGroup):
    RE_recipe_name = State()
    RE_select_ingredient = State()
    RE_weight = State()

class IngredientStates(StatesGroup):
    IN_product_name = State()        # Input by user (add simurarity check ??)
    IN_relation_to_water = State()   # Select from list. (constans 10 options 1 - 1/10)
    IN_shop_name = State()           # Select from list. Load list from shops_list.csv
    IN_stats = State()               # Price Wheight Calories protein fat carbs

class StandaloneStates(StatesGroup):
    SA_product_name = State()
    SA_shop_name = State()
    SA_stats = State()