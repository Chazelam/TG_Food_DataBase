from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, InlineKeyboardButton

async def create_reply_keyboard(button_list: list[str], n_in_row: int = 3):
    keyboard = ReplyKeyboardBuilder()
    for button in button_list:
        keyboard.add(KeyboardButton(text = button))
    return keyboard.adjust(n_in_row).as_markup()


choice_what_to_add = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Standalone',
                                  callback_data="add_standalone"),
             InlineKeyboardButton(text='Ingredient',
                                  callback_data="add_ingredient")],
             [InlineKeyboardButton(text='Recipe',
                                  callback_data="add_recipe")]])

recipe_summary = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='add ingredient',
                                  callback_data="add_ingredient_in_recipe"),
             InlineKeyboardButton(text='Save recipe',
                                  callback_data="save_new_recipe")]])

save_ingredient = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Yes',
                                  callback_data="save_new_ingredient"),
             InlineKeyboardButton(text='No',
                                  callback_data="dont_save")]])

save_standalone = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Yes',
                                  callback_data="save_new_standalone"),
             InlineKeyboardButton(text='No',
                                  callback_data="dont_save")]])

