from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from .states import IngredientStates

import app.keyboards as kb
import app.database.requests as req

router = Router()

@router.callback_query(F.data.in_(["add_ingredient"]))
async def start_ingredient_creation(callback: CallbackQuery, state: FSMContext):
    """Handler to initiate ingredient creation flow"""
    await callback.answer()
    await callback.message.edit_text(text='Enter product name')
    await state.set_state(IngredientStates.IN_product_name)

@router.message(StateFilter(IngredientStates.IN_product_name))
async def handle_product_name(message: Message, state: FSMContext):
    """Process product name and request water ratio"""
    # TODO: Add duplicate check against database
    await state.update_data(product_name=message.text)
    await message.answer(
        text=f"✅ Product '{message.text}' added\n\nSelect water ratio:",
        reply_markup=await kb.create_reply_keyboard([f"{x/10:.1f}" for x in range(10, 0, -1)]))
    await state.set_state(IngredientStates.IN_relation_to_water)






@router.message(StateFilter(IngredientStates.IN_relation_to_water))
async def handle_water_ratio(message: Message, state: FSMContext):
    """Process water ratio and request shop selection"""
    # Add validation for ratio format (0.1-1.0)
    await state.update_data(relation_to_water=message.text)
    await message.answer(
        text="Select shop:",
        reply_markup=await kb.create_reply_keyboard(await req.get_shop_list()))
    await state.set_state(IngredientStates.IN_shop_name)

@router.message(StateFilter(IngredientStates.IN_shop_name))
async def handle_shop_selection(message: Message, state: FSMContext):
    """Process shop selection and request nutrition data"""
    shop_list = await req.get_shop_list()
    try:
        shop_id = str(shop_list.index(message.text) + 1)  # Consider using actual shop IDs from DB
        await state.update_data(shop=shop_id)
    except ValueError:
        await message.answer("⚠️ Shop not found. Please select from the list.")
        return  # Maintain current state for retry

    await message.answer(
        text="Enter nutritional values (space-separated):\n"
             "Price, Weight(g), Calories, Proteins, Fats, Carbs\n"
             "Example: 5.99 500 350 25 10 60",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(IngredientStates.IN_stats)

@router.message(StateFilter(IngredientStates.IN_stats))
async def handle_nutrition_data(message: Message, state: FSMContext):
    """Validate and display ingredient summary before saving"""
    try:
        # Basic input validation
        stats = [float(x) for x in message.text.replace(",", ".").split()]
        if len(stats) != 6:
            raise ValueError("Invalid number of parameters")
             
        await state.update_data(stats=stats)
        collected_data = await state.get_data()
        
        # Build confirmation message
        summary = (
            f"📝 Confirm details:\n"
            f"Name: {collected_data['product_name']}\n"
            f"Water Ratio: {collected_data['relation_to_water']}\n"
            f"Shop: {collected_data['shop']}\n"
            f"Price: ${stats[0]:.2f}\n"
            f"Weight: {stats[1]}g\n"
            f"Calories: {stats[2]}kcal\n"
            f"Proteins: {stats[3]}g\n"
            f"Fats: {stats[4]}g\n"
            f"Carbs: {stats[5]}g"
        )
        
        await message.answer(summary, reply_markup=kb.save_ingredient)
        
    except (ValueError, IndexError) as e:
        await message.answer("❌ Invalid format. Please enter 6 numeric values separated by spaces.")
        print(f"Validation error: {e}")

@router.callback_query(F.data.in_(["save_new_ingredient"]))
async def save_ingredient(callback: CallbackQuery, state: FSMContext):
    """Save validated ingredient to database"""
    await callback.answer()
    collected_data = await state.get_data()
    try:
        await req.save_ingredient(collected_data)
        await state.clear()
        await callback.message.edit_text(
            text="✅ Product saved to database",
            reply_markup=kb.add_another_ingredient)
    except Exception as e:
        await callback.message.answer("⚠️ Error saving product. Please try again.")
        print(f"Database error: {e}")

@router.callback_query(F.data.in_(["dont_save"]))
async def cancel_creation(callback: CallbackQuery, state: FSMContext):
    """Cancel ingredient creation process"""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("❌ Product creation canceled")