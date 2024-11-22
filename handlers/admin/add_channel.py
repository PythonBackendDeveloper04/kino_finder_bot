from loader import bot, dp, db
from filters import IsBotAdmin, IsPrivate
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from states.states import AddChannelState
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from keyboards.default.buttons import back_button, admin_buttons
from aiogram.filters.callback_data import CallbackData


# CheckAddChannel faqat `channel_id`ni ishlatadi
class CheckAddChannel(CallbackData, prefix="ikb4"):
    channel_id: str


# 🗣 Kanal qo'shish uchun xabar yuborilganda
@dp.message(F.text == "🗣 Kanal qo'shish", IsBotAdmin(), IsPrivate())
async def add_channel(message: types.Message, state: FSMContext):
    await message.answer("Kanal ID sini yuboring!", reply_markup=back_button())
    await state.set_state(AddChannelState.channnel_id)


# Kanal ID yuborilganda
@dp.message(F.text, IsBotAdmin(), IsPrivate(), AddChannelState.channnel_id)
async def add_channel_state(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("🔝 Admin panel!", reply_markup=admin_buttons())
        await state.clear()
    else:
        try:
            # Kanal ma'lumotlarini olish
            channel = await bot.get_chat(chat_id=message.text)
            if channel.type == "channel":
                title = channel.title
                link = await channel.export_invite_link()
                try:
                    subscribers = await bot.get_chat_member_count(chat_id=message.text)
                    subscribers = str(subscribers)
                except Exception as e:
                    print(e)
                    subscribers = "0"

                # Holat mashinasiga ma'lumotlarni yozib qo'yish
                await state.update_data(
                    channel_id=message.text,
                    channel_name=title,
                    channel_subscribers=subscribers,
                )

                # Tugma yaratish
                btn = InlineKeyboardBuilder()
                btn.add(InlineKeyboardButton(text=title, url=link))
                btn.button(
                    text="Kanalni qo'shish va tasdiqlash",
                    callback_data=CheckAddChannel(channel_id=message.text),
                )
                btn.adjust(1, 1)

                # Tasdiqlashni so'rash
                await message.answer("Kanalni tasdiqlaysizmi?", reply_markup=btn.as_markup())
                await state.set_state(AddChannelState.check)
            else:
                await message.answer("Kanal ID sini yuboring!", reply_markup=back_button())
                await state.set_state(AddChannelState.channnel_id)
        except Exception as e:
            print(e)
            await message.answer("Iltimos botni kanalga admin qiling!", reply_markup=back_button())
            await state.set_state(AddChannelState.channnel_id)


# Kanalni tasdiqlash va qo'shish
@dp.callback_query(CheckAddChannel.filter(), IsBotAdmin(), AddChannelState.check)
async def get(call: types.CallbackQuery, callback_data: CheckAddChannel, state: FSMContext):
    await call.answer("Kanal qo'shildi", show_alert=True)

    # Holatdan ma'lumotlarni olish
    data = await state.get_data()
    channel_id = callback_data.channel_id
    channel_name = data.get("channel_name")
    channel_subscribers = data.get("channel_subscribers")

    # Kanalni ma'lumotlar bazasiga qo'shish
    await db.add_channel(
        channel_id=channel_id,
        channel_name=channel_name,
        channel_members_count=channel_subscribers
    )

    # Admin paneliga qaytish
    await call.message.answer("🔝 Admin panel!", reply_markup=admin_buttons())
    await call.message.delete()
    await state.clear()
