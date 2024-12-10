from aiogram import BaseMiddleware, types
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery, Update
from typing import Any
from loader import bot, db
from utils.misc.subscription_checker import check
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
import os

class CheckSubs(CallbackData, prefix="ikb3"):
    check: bool

DEFAULT_RATE_LIMIT = 0.1

class UserCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Any, data: dict):
        user_id = None

        # Event turi bo‘yicha tekshirish
        if isinstance(event, Message) and event.text:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        else:
            # Agar event turi noma’lum bo‘lsa, middlewareni keyingisiga uzatadi
            return await handler(event, data)

        # Obunani tekshirishni boshlash
        final_status = True
        builder = InlineKeyboardBuilder()
        channels = await db.select_all_channels()
        instagram_profiles = await db.select_all_instagram_profiles()

        # Telegram kanallarini tekshirish
        for channel in channels:
            try:
                status = await check(user_id=user_id, channel=channel[2])
                final_status *= status

                chat = await bot.get_chat(channel[2])  # Chat detallarini olishga harakat qiladi
                invite_link = await db.invite_link(chat.id)
                if status:
                    builder.button(text=f"✅ {chat.title}", url=invite_link)
                else:
                    builder.button(text=f"❌ {chat.title}", url=invite_link)
            except Exception as e:
                print(f"Error checking channel {channel[2]}: {e}")

        # Instagram profillarini ko‘rsatish
        for profile in instagram_profiles:
            try:
                # Instagram profile linklarini faqat botdagi asosiy foydalanuvchi uchun ko‘rsatadi
                builder.button(text=f"Instagram: {profile['name']}", url=f"https://www.instagram.com/{profile['link']}")
            except Exception as e:
                print(f"Error checking Instagram profile {profile['link']}: {e}")

        # Obuna tekshirish xabari
        text = "Obunani tekshirish"
        builder.button(text=text, callback_data=CheckSubs(check=True))
        builder.adjust(1)

        if not final_status:
            await bot.send_message(
                chat_id=user_id,
                text="Iltimos, bot to'liq ishlashi uchun quyidagi kanallarga va Instagram profillarga obuna bo'ling!",
                reply_markup=builder.as_markup(),
            )
        else:
            return await handler(event, data)
