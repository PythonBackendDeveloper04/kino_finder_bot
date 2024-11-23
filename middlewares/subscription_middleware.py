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

class CheckSubsCall(CallbackData, prefix="ikb25"):
    test: str

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

        for CHANNEL in channels:
            status = await check(user_id=user_id, channel=CHANNEL[2])
            final_status *= status  # Final statusni yangilash
            print(status)

            channel = await bot.get_chat(CHANNEL[2])
            try:
                # Kanal uchun tugma qo‘shish
                if status:
                    builder.button(text=f"✅ {channel.title}", url=f"{channel.invite_link}")
                    print("Kanalga obuna bo‘lgan")
                else:
                    builder.button(text=f"❌ {channel.title}", url=f"{channel.invite_link}")
                    print("Kanalga obuna emas")
            except Exception as e:
                print(f"Kanalni olishda xatolik: {e}")

        # Obuna tekshirish xabari
        text = "Obunani tekshirish"
        builder.button(text=text, callback_data=CheckSubs(check=True))
        builder.adjust(1)

        if not final_status:
            # Agar foydalanuvchi barcha kanallarga obuna bo‘lmagan bo‘lsa
            await bot.send_message(
                chat_id=user_id,
                text="Iltimos, bot to'liq ishlashi uchun quyidagi kanallarga obuna bo'ling!",
                reply_markup=builder.as_markup(),
            )
        else:
            # Obuna muammosi yo‘q, asosiy handlerni chaqirish
            return await handler(event, data)
