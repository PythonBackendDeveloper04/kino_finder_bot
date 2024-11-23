from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ChooseLanguageCallback(CallbackData,prefix='ikb01'):
    language : str

button = InlineKeyboardBuilder()
button.button(text="🇺🇿 O'zbek tili",callback_data=ChooseLanguageCallback(language='uz'))
button.button(text="🇬🇧 English",callback_data=ChooseLanguageCallback(language='en'))
button.adjust(1)