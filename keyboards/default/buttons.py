from aiogram.utils.keyboard import ReplyKeyboardBuilder
def admin_buttons():
    btn = ReplyKeyboardBuilder()
    btn.button(text="🎞 Kino qo'shish")
    btn.button(text="🗣 Reklama yuborish")
    btn.button(text="📊 Obunachilar soni")
    btn.button(text="📢 Kanal qo'shish")
    btn.button(text="❌ Kanal o'chirish")
    btn.button(text="📢 Kanallar")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True,input_placeholder="Kerakli bo'limni tanlang...",
                         one_time_keyboard=True)
def add_type():
    btn = ReplyKeyboardBuilder()
    btn.button(text="✏️ Matn")
    btn.button(text="📸 Rasm")
    btn.button(text="📹 Video")
    btn.button(text="🔙 Orqaga")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)

def back_button():
    btn = ReplyKeyboardBuilder()
    btn.button(text="◀️ Orqaga")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)
def get_before_url():
    btn = ReplyKeyboardBuilder()
    btn.button(text="⏺ Bekor qilish")
    btn.button(text="🆗 Kerakmas")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)
def send_button():
    btn = ReplyKeyboardBuilder()
    btn.button(text="⏺ Bekor qilish")
    btn.button(text="📤 Yuborish")
    btn.adjust(2)
    return btn.as_markup(resize_keyboard=True)