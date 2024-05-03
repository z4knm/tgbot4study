from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Privet')],
									[KeyboardButton(text='Vtoraya str')],
									[KeyboardButton(text='Pervaya ch'),
									KeyboardButton(text='Vtoraya ch')]],
									input_field_placeholder='Viberite punkt menu...')