from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton 

start = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Замены на завтра')],
									[KeyboardButton(text='Расписание')],
									[KeyboardButton(text='Время звонков')],
									[KeyboardButton(text='Прочие графики'),
									KeyboardButton(text='Полезные ссылки')]],
									input_field_placeholder='Выберите пункт меню...')

urls = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Официальный Сайт', url='https://pgups-karelia.ru')],
											[InlineKeyboardButton(text='Группа ВКонтакте', url='https://vk.com/pf_pgups')],
											[InlineKeyboardButton(text='Moodle', url='http://212.109.2.247/login/index.php')]
											])

grphs = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Расписание учебных недель', callback_data='uchned')],
											[InlineKeyboardButton(text='График проведения консультаций', callback_data='grkon')],
											[InlineKeyboardButton(text='Расписание промежуточной аттестации', callback_data='rprat')]
											])