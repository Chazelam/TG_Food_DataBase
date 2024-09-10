from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.formatting import Text
import asyncio

import app.keyboards as kb
import app.database.requests as req

from tabulate import tabulate

command_show_router = Router()

@command_show_router.message(Command(commands='show'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    
        
    ingredient_list = await req.get_ingredient_list()
    # ^ return dict: {ingredient_name: [Calories per gram, Price per gramm, proteins per gram, fats per gram, carbs per gram]}
    recipies: dict[str:list] = {}
    for entry in list(await req.show_reecipes()):
        try:
            recipies[entry.recipe_name].append([entry.ingredient, entry.weight,
                                                 round(float(entry.weight)*ingredient_list[entry.ingredient][0], 2)])
        except:
            recipies[entry.recipe_name] = []
            recipies[entry.recipe_name].append([entry.ingredient, entry.weight,
                                                 round(float(entry.weight)*ingredient_list[entry.ingredient][0], 2)])
    print(recipies)
    for recipe_name in recipies.keys():
        recipe = recipies[recipe_name]
        header = ["Ingridient", "weight", "Calories"]
        # await message.answer(text = f"```{fmt[i]}\n{t[i]}```", parse_mode="Markdown")

        stats_sum = {"price": 0, "calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
        for ingredient in recipe:
            stats_sum["calories"] += ingredient[2]
            stats_sum["price"] += round(float(ingredient[1])*ingredient_list[ingredient[0]][1], 2)
            stats_sum["proteins"] += round(float(ingredient[1])*ingredient_list[ingredient[0]][2], 2)
            stats_sum["fats"] += round(float(ingredient[1])*ingredient_list[ingredient[0]][3], 2)
            stats_sum["carbs"] += float(ingredient[1])*ingredient_list[ingredient[0]][4]

        await message.answer(text=f"{recipe_name}```Recipe\n{tabulate(recipe, header, tablefmt="pretty")}\n```"
                              f"Price: {round(stats_sum["price"], 2)}р.\n"
                              f"Calories: {round(stats_sum["calories"], 2)}\n"
                              f"Value: {round(stats_sum["calories"]/stats_sum["price"], 2)}\n\n"

                              f"proteins: {round(stats_sum["proteins"], 2)}\n"
                              f"fats: {round(stats_sum["fats"], 2)}\n"
                              f"carbs: {round(stats_sum["carbs"], 2)}\n",
                        parse_mode="Markdown")
    