from app.database.models import async_session
from app.database.models import Shops, Ingredients, Standalone, Recipes
from sqlalchemy import select

async def get_shop_list():
    async with async_session() as session:
        return [x.shop_name for x in await session.scalars(select(Shops))]

# return dict: {ingredient_name: [Calories per gram, Price per gramm, proteins per gram, fats per gram, carbs per gram]}
async def get_ingredient_list():
    ingredient_list = {}
    async with async_session() as session:
        for x in await session.scalars(select(Ingredients)):
            entry = [round((float(x.calories)*float(x.relation_to_water))/100, 2),          # Calories per gram
                     round((float(x.price)*float(x.relation_to_water))/float(x.weight), 2), # Price per gramm
                     round((float(x.proteins)*float(x.relation_to_water))/100, 2),          # proteins per gram
                     round((float(x.fats)*float(x.relation_to_water))/100, 2),              # fats per gram
                     round((float(x.carbs)*float(x.relation_to_water))/100, 2)              # carbs per gram
                     ]
            ingredient_list[x.ingredient_name] = entry
        return ingredient_list


async def save_ingredient(collected_data: dict):
    async with async_session() as session:
        session.add(Ingredients(ingredient_name =   collected_data['product_name'],
                                relation_to_water = collected_data['relation_to_water'],
                                shop =              collected_data['shop'],
                                price =             collected_data['stats'][0],
                                weight =            collected_data['stats'][1],
                                calories =          collected_data['stats'][2],
                                proteins =          collected_data['stats'][3],
                                fats =              collected_data['stats'][4],
                                carbs =             collected_data['stats'][5]))
        await session.commit()


async def save_sandalone(collected_data: dict):
    async with async_session() as session:
        session.add(Standalone(ingredient_name = collected_data['product_name'],
                               shop =     collected_data['shop'],
                               price =    collected_data['stats'][0],
                               weight =   collected_data['stats'][1],
                               calories = collected_data['stats'][2],
                               proteins = collected_data['stats'][3],
                               fats =     collected_data['stats'][4],
                               carbs =    collected_data['stats'][5]))
        await session.commit()


async def save_new_recipe(recipe_name: str, recipe: dict):
    async with async_session() as session:
        for ingredient in recipe:
            session.add(Recipes(recipe_name = recipe_name,
                                ingredient = ingredient,
                                weight = recipe[ingredient]))
        await session.commit()


    #     recipe_name: Mapped[str] = mapped_column(String(25))
    # ingredient: Mapped[str] = mapped_column(String(25))
    # weight: Mapped[str] = mapped_column(String(25))
