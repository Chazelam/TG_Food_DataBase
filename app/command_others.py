from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

command_others_router = Router()


@command_others_router.message(Command(commands='start'))
async def process_add_command(message: Message, state: FSMContext):
    await message.answer(text = "What")

