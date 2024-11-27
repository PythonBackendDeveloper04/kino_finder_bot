from loader import bot,dp,db
from aiogram.filters import CommandStart,Command
from aiogram.filters.callback_data import CallbackData
from aiogram import types,F
from keyboards.inline.buttons import button,ChooseLanguageCallback
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton
from utils.misc.subscription_checker import check
import re

class CheckSubs(CallbackData,prefix='ikb3'):
    check:bool

@dp.message(CommandStart())
async def start(message:types.Message):
    try:
       await db.add_user(fullname=message.from_user.full_name,telegram_id=message.from_user.id)
    except Exception as e:
        print(e)
    btn = InlineKeyboardBuilder()
    channels = await db.select_all_channels()
    final_status = True
    for channel in channels:
        status = True
        try:
            status = await check(user_id=message.from_user.id,
                                 channel=channel[2]) # Foydalanuvchining kanalga obunasi tekshiriladi.
        except Exception as e:
            print(e)
            status = False
        final_status *= status
        try:
            channel = await bot.get_chat(channel[2]) # Kanal ma'lumotlarini olish.
            invite_link = await db.invite_link(channel.id)  # Taklif havolasini olish
            print(f"invite_link:{invite_link}")
            if not status: # Agar foydalanuvchi kanalga obuna bo'lmasa:
                btn.row(InlineKeyboardButton(text=f"❌ {channel.title}", url=invite_link))
        except Exception as e:
            print(e)
    btn.button(text="Obunani tekshirish", callback_data=CheckSubs(check=True)) # Obuna holatini tekshirish tugmasi.
    btn.adjust(1)
    if final_status: # Agar barcha kanallarga obuna bo'lsa:
        await message.answer(f'Assalomu aleykum <b>{message.from_user.first_name}</b>')
        await message.answer("Kino kodini yuboring:")

    else:
        await message.answer(text=
                             f"Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!",
                             reply_markup=btn.as_markup(row_width=1))
@dp.callback_query(CheckSubs.filter())
async def test(call:types.CallbackQuery):
    await call.answer(cache_time=60) # Callbackni javob berish vaqti
    user_id = call.from_user.id #foydalanuvchi idsini olish
    channels = await db.select_all_channels() #ma'lumotlar kanallarni olish
    buttons = [] #tugmalar ro'yhati
    all_subscribed = True
    for channel in channels:
        try:
            chat = await bot.get_chat(channel[2]) # kanal msa'lumotlarini olish
            invite_link = await db.invite_link(chat.id)
            res = await bot.get_chat_member(chat_id=channel[2], user_id=user_id) # Foydalanuvchining obuna holatini tekshirish.
            if res.status in ['member', 'administrator', 'creator']: #agar obunasi bo'lsa:
                buttons.append(InlineKeyboardButton(text=f"✅ {chat.title}", url=invite_link))
                print(f"invite_link:{invite_link}")
            else:
                buttons.append(InlineKeyboardButton(text=f"❌ {chat.title}", url=invite_link))
                all_subscribed = False
        except Exception as e:
            print(e)

    builder = InlineKeyboardBuilder()
    builder.add(*buttons)
    builder.button(text="Obunani tekshirish", callback_data=CheckSubs(check=True))
    builder.adjust(1)

    if not all_subscribed: # Agar obunalar yetarli bo'lmasa:
        await bot.send_message(
            chat_id=user_id,
            text="Iltimos bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!",
            reply_markup=builder.as_markup()
        )
    else:
        await bot.send_message(chat_id=user_id,
                               text="<i>Kino kodini kiriting:</i>")

    try:
        await call.message.delete()
    except Exception as e:
        print(e)

@dp.message()
async def get_movie(message:types.Message):
    code = message.text
    movie = await db.select_movie(code=code)
    if not movie:
        await message.answer("Bunaqa kodli kino topilmadi")
        return

        # `movie` ichidagi `post_id` maydonini olish
    post_id = movie["post_id"]  # yoki `movie.get("post_id")`

    # `post_id` dan URL o'rniga faqat `message_id` ni olish
    match = re.search(r'/(\d+)$', post_id)
    print(match)
    if match:
        try:
            message_id = int(match.group(1))
            print(message_id)
            await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id="@ChannelMovieTest",
                message_id=message_id
            )
        except Exception as e:
            print(e)
    else:
        await message.answer("Xato: URL dan message_id ajratib bo'lmadi!")