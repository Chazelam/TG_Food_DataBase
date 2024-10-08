from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.formatting import Text
from tabulate import tabulate

import app.keyboards as kb
import app.database.requests as req

command_add_router = Router()
storage = MemoryStorage() # FSM shit

# Class for FSM
class FSMFillForm(StatesGroup):
    # Standalone
    SA_product_name = State() # Input by user (add simurarity check ??)
    SA_shop_name    = State() # Select from list. Load list from shops_list.csv
    SA_stats        = State() # Price Wheight Calories protein fat carbs
    # Ingredient
    IN_product_name = State()      # Input by user (add simurarity check ??)
    IN_relation_to_water = State() # Select from list. (constans 10 options 1 - 1/10)
    IN_shop_name    = State()      # Select from list. Load list from shops_list.csv
    IN_stats        = State()      # Price Wheight Calories protein fat carbs
    # Recipe
    RE_recipe_name = State()
    RE_select_ingredient = State()
    RE_weight = State()
    RE_summary = State()



@command_add_router.message(Command(commands='add'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    await message.answer(text = "What you wanna add ?",
                         reply_markup = kb.choice_what_to_add)

@command_add_router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text="You not doing anything")

@command_add_router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text="Cancel")
    await state.clear()


### Add Recipe ###
@command_add_router.callback_query(F.data.in_(["add_recipe"]))
async def add_new_recipe(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    ingredient_list = await req.get_ingredient_list()
    # ^ return dict: {ingredient_name: [Calories per gram, Price per gramm, proteins per gram, fats per gram, carbs per gram]}
    remaining = ingredient_list.keys()
    await state.update_data(recipe_name = "",
                            ingredient_list = ingredient_list, 
                            remaining = remaining, 
                            recipe = {},
                            current_ingredient = "")

    await callback.message.edit_text(text = f"Loaded {len(remaining)} ingredients\n\nName of recipe")
    await state.set_state(FSMFillForm.RE_recipe_name)


@command_add_router.message(StateFilter(FSMFillForm.RE_recipe_name))
async def select_ingredient(message: Message, state: FSMContext):
    collected_data = await state.get_data()
    await state.update_data(recipe_name = message.text)
    await message.answer(text=f"Recipe name - {message.text}\nSelect new ingredient",
                         reply_markup = await kb.create_reply_keyboard(collected_data["remaining"]))
    
    await state.set_state(FSMFillForm.RE_select_ingredient)


@command_add_router.message(StateFilter(FSMFillForm.RE_select_ingredient))
async def fill_weight(message: Message, state: FSMContext):
    # Save selected ingredient
    ingredient = message.text
    await state.update_data(current_ingredient = ingredient)
    # Remove ingredient from remaining
    collected_data = await state.get_data()
    remaining = list(collected_data["remaining"])
    remaining.remove(ingredient)
    await state.update_data(remaining = remaining)
    
    await message.answer(text=f"How much {ingredient} needed ?\nSend weight in gramms.",
                         reply_markup = ReplyKeyboardRemove())
    
    await state.set_state(FSMFillForm.RE_weight)



@command_add_router.message(StateFilter(FSMFillForm.RE_weight))
async def summary_of_recipe(message: Message, state: FSMContext):

    collected_data = await state.get_data()
    recipe: dict = collected_data["recipe"]
    recipe[collected_data["current_ingredient"]] = message.text

    ingredient_list = collected_data["ingredient_list"]
    # ^ return dict: {ingredient_name: [Calories per gram, Price per gramm, proteins per gram, fats per gram, carbs per gram]}

    # summary_text = [f"{(recipe[ingredient]+"г.").ljust(7)}{ingredient.ljust(26)}{round(float(recipe[ingredient])*ingredient_list[ingredient][0], 2)}" for ingredient in recipe.keys()]
    summary_text = []
    stats_sum = {"price": 0, "calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
    for ingredient in recipe.keys():
        weight = recipe[ingredient]
        ingredient_name = ingredient
        calories = round(float(recipe[ingredient])*ingredient_list[ingredient][0], 2)

        stats_sum["calories"] += round(float(recipe[ingredient])*ingredient_list[ingredient][0], 2)
        stats_sum["price"] += round(float(recipe[ingredient])*ingredient_list[ingredient][1], 2)
        stats_sum["proteins"] += round(float(recipe[ingredient])*ingredient_list[ingredient][2], 2)
        stats_sum["fats"] += round(float(recipe[ingredient])*ingredient_list[ingredient][3], 2)
        stats_sum["carbs"] += round(float(recipe[ingredient])*ingredient_list[ingredient][4], 2)
        

        summary_text.append([weight, ingredient_name, calories])

    await message.answer(text=f"```Recipe\n{tabulate(summary_text, headers=["Wheight","Ingredient", "Calories"], tablefmt="pretty")}\n```"
                              f"Price: {stats_sum["price"]}р.\n"
                              f"Calories: {stats_sum["calories"]}\n"
                              f"Value: {round(stats_sum["calories"]/stats_sum["price"], 2)}\n\n"

                              f"proteins: {stats_sum["proteins"]}\n"
                              f"fats: {stats_sum["fats"]}\n"
                              f"carbs: {stats_sum["carbs"]}\n",
                        reply_markup=kb.recipe_summary, parse_mode="Markdown")
    
    await state.set_state(FSMFillForm.RE_select_ingredient)



@command_add_router.callback_query(F.data.in_(["add_ingredient_in_recipe"]))
async def select_ingredient2(callback: CallbackQuery, state: FSMContext):
    collected_data = await state.get_data()
    # print(collected_data["remaining"])
    # print(collected_data)
    await callback.answer()
    await callback.message.answer(text=f"Select new ingredient",
                         reply_markup = await kb.create_reply_keyboard(collected_data["remaining"]))
    
    await state.set_state(FSMFillForm.RE_select_ingredient)

@command_add_router.callback_query(F.data.in_(["save_new_recipe"]))
async def process_buttons_press(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    collected_data = await state.get_data()
    recipe_name = collected_data["recipe_name"]
    recipe: dict = collected_data["recipe"]
    await req.save_new_recipe(recipe_name, recipe)
    await state.clear()
    await callback.message.edit_text(text = "Recipe saved in databate",
                                     reply_markup=kb.add_another_recipe)


# table = [["Sun",696000,1989100000],["Earth",6371,5973.6],
#          ["Moon",1737,73.5],["Mars",3390,641.85]]

# fmt = ["plain", "simple", "github", "grid", "simple_grid", "rounded_grid", "heavy_grid", "mixed_grid", "double_grid", "fancy_grid", "outline", "simple_outline", "rounded_outline", "heavy_outline", "mixed_outline", "double_outline", "fancy_outline", "pipe", "orgtbl", "asciidoc", "jira", "presto", "pretty", "psql", "rst", "mediawiki", "moinmoin", "youtrack", "html", "unsafehtml", "latex", "latex_raw", "latex_booktabs", "latex_longtable", "textile", "tsv"]
# t = [tabulate(table, headers=["Planet","R (km)", "mass (x 10^29 kg)"], tablefmt=x) for x in fmt]
# ljust(10)
# Recipe summary:
# 100г. Рис                       100ккал
# 100г. Курица                 200ккал
# 70г.   Сыр              
# 100г. Хлеб             
# 30г.   Масло          


# Price: 106р.
# Calories: 400
# Value: 14.5

# proteins: 10
# fats: 4
# carbs: 72










### Add Ingredient ###

@command_add_router.callback_query(F.data.in_(["add_ingredient"]))
async def process_fillform_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(text='Enter product name')
    await state.set_state(FSMFillForm.IN_product_name)

@command_add_router.message(StateFilter(FSMFillForm.IN_product_name))
async def process_relation_to_water(message: Message, state: FSMContext):
    await state.update_data(product_name = message.text)
    await message.answer(text=f"Great, we add product named {message.text}\n\nNow select it's relation to water.",
                         reply_markup = await kb.create_reply_keyboard([str(x/10) for x in range(10, 0, -1)]))
    
    await state.set_state(FSMFillForm.IN_relation_to_water)

@command_add_router.message(StateFilter(FSMFillForm.IN_relation_to_water))
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(relation_to_water = message.text)
    await message.answer(text=f"Now select shop.",
                         reply_markup = await kb.create_reply_keyboard(await req.get_shop_list()))
    
    await state.set_state(FSMFillForm.IN_shop_name)


@command_add_router.message(StateFilter(FSMFillForm.IN_shop_name))
async def process_gender_press(message: Message, state: FSMContext):
    shop_list = await req.get_shop_list()
    try:
        await state.update_data(shop = str(shop_list.index(message.text) + 1))
    except ValueError:
        await message.answer(text = "Shop is not found")
    await message.answer(
            text = "Ok, now 'hard' part.\n"
                   "Please enter stats of the product in this order:\n"
                   "Price, Wheight, Calories, protein, fat, carbs",
            reply_markup = ReplyKeyboardRemove())

    await state.set_state(FSMFillForm.IN_stats)

@command_add_router.message(StateFilter(FSMFillForm.IN_stats))
async def process_wish_news_press(message: Message, state: FSMContext):
    await state.update_data(stats = message.text.replace(", ", " ").replace(",", ".").split())
    collected_data = await state.get_data()

    await message.answer(
        text = f"Save:\n"
               f"Product name: {collected_data['product_name']}\n"
               f"Relation to water: {collected_data['relation_to_water']}\n"
               f"Shop: {collected_data['shop']}\n"
               f"Price: {collected_data['stats'][0]}\n"
               f"Weight: {collected_data['stats'][1]}\n"
               f"Calories: {collected_data['stats'][2]}\n"
               f"Proteins: {collected_data['stats'][3]}\n"
               f"Fats: {collected_data['stats'][4]}\n"
               f"Carbs: {collected_data['stats'][5]}\n",
        reply_markup = kb.save_ingredient)
    print(collected_data)


@command_add_router.callback_query(F.data.in_(["save_new_ingredient"]))
async def process_buttons_press(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    collected_data = await state.get_data()
    await req.save_ingredient(collected_data)
    await state.clear()
    await callback.message.edit_text(text = "Product saved in databate",
                                     reply_markup=kb.add_another_ingredient)

@command_add_router.callback_query(F.data.in_(["dont_save"]))
async def process_buttons_press(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(text = "Product don't saved in databate")












### Add Standalone ###

@command_add_router.callback_query(F.data.in_(["add_standalone"]))
async def process_fillform_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(text='Enter product name')
    await state.set_state(FSMFillForm.SA_product_name)

@command_add_router.message(StateFilter(FSMFillForm.SA_product_name))
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(product_name = message.text)
    await message.answer(text=f"Great, we add product named {message.text}\n\nNow select shop.",
                         reply_markup = await kb.create_reply_keyboard(await req.get_shop_list()))
    
    await state.set_state(FSMFillForm.SA_shop_name)


@command_add_router.message(StateFilter(FSMFillForm.SA_shop_name))
async def process_gender_press(message: Message, state: FSMContext):
    shop_list = await req.get_shop_list()
    try:
        await state.update_data(shop = str(shop_list.index(message.text) + 1))
    except ValueError:
        await message.answer(text = "Shop is not found")
    await message.answer(
            text = "Ok, now 'hard' part.\n"
                   "Please enter stats of the product in this order:\n"
                   "Price, Wheight, Calories, protein, fat, carbs",
            reply_markup = ReplyKeyboardRemove())

    await state.set_state(FSMFillForm.SA_stats)

@command_add_router.message(StateFilter(FSMFillForm.SA_stats))
async def process_wish_news_press(message: Message, state: FSMContext):
    await state.update_data(stats = message.text.replace(", ", " ").replace(",", ".").split())
    collected_data = await state.get_data()

    await message.answer(
        text = f"Save:\n"
               f"Product name: {collected_data['product_name']}\n"
               f"Shop: {collected_data['shop']}\n"
               f"Price: {collected_data['stats'][0]}\n"
               f"Weight: {collected_data['stats'][1]}\n"
               f"Calories: {collected_data['stats'][2]}\n"
               f"Proteins: {collected_data['stats'][3]}\n"
               f"Fats: {collected_data['stats'][4]}\n"
               f"Carbs: {collected_data['stats'][5]}\n",
        reply_markup = kb.save_standalone)
    print(collected_data)


@command_add_router.callback_query(F.data.in_(["save_new_standalone"]))
async def process_buttons_press(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    collected_data = await state.get_data()
    await req.save_sandalone(collected_data)
    await state.clear()
    await callback.message.edit_text(text = "Product saved in databate",
                                     reply_markup=kb.add_another_standalone)

@command_add_router.callback_query(F.data.in_(["dont_save"]))
async def process_buttons_press(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(text = "Product don't saved in databate")


