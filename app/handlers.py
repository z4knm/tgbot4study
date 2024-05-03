from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
	await message.answer('Privet!', reply_markup=kb.start)


@router.message(Command('help'))
async def cmd_help(message: Message):
	await message.answer('Help button')