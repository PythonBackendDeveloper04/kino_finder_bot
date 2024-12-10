from loader import bot, dp, db
from filters import IsBotAdmin, IsPrivate
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from states.states import AddChannelState,AddInstagramProfile
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from keyboards.default.buttons import back_button, admin_buttons,add_channel_or_insProfile
from aiogram.filters.callback_data import CallbackData
import urllib.parse
import hashlib


class CheckAddChannel(CallbackData, prefix="ikb4"):
    channel_id: str
class CheckAddInstagramProfile(CallbackData, prefix="ikb8"):
    link: str

@dp.message(F.text=="📢 Kanal qo'shish")
async def func(message:types.Message):
    await message.answer("Telegram kanal qo'shasizmi? yoki Instagram profil?",reply_markup=add_channel_or_insProfile())


@dp.message(F.text == "◀️ Orqaga")
async def back(message:types.Message):
    await message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())

@dp.message(F.text == "Telegram", IsBotAdmin(), IsPrivate())
async def add_channel(message: types.Message, state: FSMContext):
    await message.answer("Kanal ID sini yuboring!", reply_markup=back_button())
    await state.set_state(AddChannelState.channel_id)

@dp.message(F.text, IsBotAdmin(), IsPrivate(), AddChannelState.channel_id)
async def add_channel_state(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
        await state.clear()
    else:
        try:
            # Kanal ma'lumotlarini olish
            channel = await bot.get_chat(chat_id=message.text)
            if channel.type == "channel":
                title = channel.title

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

                await message.answer("Kanal taklif havolasini yuboring!", reply_markup=back_button())
                await state.set_state(AddChannelState.invite_link)
            else:
                await message.answer("Bu kanal emas. Kanal ID sini yuboring!", reply_markup=back_button())
        except Exception as e:
            print(e)
            await message.answer("Iltimos botni kanalga admin qiling!", reply_markup=back_button())


@dp.message(F.text, IsBotAdmin(), IsPrivate(), AddChannelState.invite_link)
async def add_invite_link(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
        await state.clear()
    else:
        try:
            # Holat mashinasiga havolani saqlash
            data = await state.get_data()
            await state.update_data(invite_link=message.text)

            # Tugma yaratish
            btn = InlineKeyboardBuilder()
            btn.add(InlineKeyboardButton(text=data['channel_name'], url=message.text))
            btn.button(
                text="✅ Tasdiqlash",
                callback_data=CheckAddChannel(channel_id=data['channel_id']),
            )
            btn.adjust(1, 1)

            await message.answer("Kanalni tasdiqlaysizmi?", reply_markup=btn.as_markup())
            await state.set_state(AddChannelState.check)
        except Exception as e:
            print(e)
            await message.answer("Yuborilgan havola noto'g'ri. Qaytadan yuboring!", reply_markup=back_button())


# Kanalni tasdiqlash va qo'shish
@dp.callback_query(CheckAddChannel.filter(), IsBotAdmin(), AddChannelState.check)
async def get(call: types.CallbackQuery, callback_data: CheckAddChannel, state: FSMContext):
    await call.answer("Kanal qo'shildi!", show_alert=True)

    # Holatdan ma'lumotlarni olish
    data = await state.get_data()
    channel_id = callback_data.channel_id
    channel_name = data.get("channel_name")
    channel_subscribers = data.get("channel_subscribers")
    invite_link = data.get("invite_link")

    # Kanalni ma'lumotlar bazasiga qo'shish
    await db.add_channel(
        channel_id=channel_id,
        channel_name=channel_name,
        channel_members_count=channel_subscribers,
        invite_link=invite_link  # Taklif havolasi qo'shildi
    )

    # Admin paneliga qaytish
    await call.message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
    await call.message.delete()
    await state.clear()

@dp.message(F.text == "Instagram", IsBotAdmin(), IsPrivate())
async def add_instagram_profile(message: types.Message, state: FSMContext):
    await message.answer("Profil nomini kiriting:", reply_markup=back_button())
    await state.set_state(AddInstagramProfile.name)


@dp.message(F.text, IsBotAdmin(), IsPrivate(), AddInstagramProfile.name)
async def add_instagram_profile_name(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
        await state.clear()
    else:
        # Profil nomini saqlash
        await state.update_data(name=message.text)

        await message.answer("Profil linkini kiriting:", reply_markup=back_button())
        await state.set_state(AddInstagramProfile.link)


@dp.message(F.text, IsBotAdmin(), IsPrivate(), AddInstagramProfile.link)
async def add_instagram_profile_link(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
        await state.clear()
    else:
        try:
            # Instagram linkini kodlash
            encoded_link = urllib.parse.quote(message.text)

            # Profil linkini saqlash
            await state.update_data(link=encoded_link)
            data = await state.get_data()

            # Tasdiqlash tugmasini yaratish
            btn = InlineKeyboardBuilder()
            btn.add(InlineKeyboardButton(text=data['name'], url=message.text))
            btn.button(
                text="✅ Tasdiqlash",
                callback_data=CheckAddInstagramProfile(link=encoded_link),
                # Kodlangan linkni callback_data'da ishlatish
            )
            btn.adjust(1, 1)

            await message.answer("Profilni tasdiqlaysizmi?", reply_markup=btn.as_markup())
            await state.set_state(AddInstagramProfile.check)
        except Exception as e:
            print(e)
            await message.answer("Yuborilgan havola noto'g'ri. Qaytadan yuboring!", reply_markup=back_button())


@dp.callback_query(CheckAddInstagramProfile.filter(), IsBotAdmin(), AddInstagramProfile.check)
async def confirm_instagram_profile(call: types.CallbackQuery, callback_data: CheckAddInstagramProfile, state: FSMContext):
    await call.answer("Instagram profil qo'shildi!", show_alert=True)

    # Holatdan ma'lumotlarni olish
    data = await state.get_data()
    name = data.get("name")
    link = callback_data.link

    # Instagram profilni ma'lumotlar bazasiga qo'shish
    await db.add_instagram_profile(
        name=name,
        link=link
    )

    # Admin paneliga qaytish
    await call.message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
    await call.message.delete()
    await state.clear()

@dp.message(F.text == "Instagram", IsBotAdmin(), IsPrivate())
async def add_instagram_profile(message: types.Message, state: FSMContext):
    await message.answer("Profil nomini kiriting:", reply_markup=back_button())
    await state.set_state(AddInstagramProfile.name)
@dp.message(F.text, IsBotAdmin(), IsPrivate(), AddInstagramProfile.name)
async def add_instagram_profile_name(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
        await state.clear()
    else:
        # Profil nomini saqlash
        await state.update_data(name=message.text)

        await message.answer("Profil linkini kiriting:", reply_markup=back_button())
        await state.set_state(AddInstagramProfile.link)
@dp.message(F.text, IsBotAdmin(), IsPrivate(), AddInstagramProfile.link)
async def add_instagram_profile_link(message: types.Message, state: FSMContext):
    if message.text == "◀️ Orqaga":
        await message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
        await state.clear()
    else:
        try:
            # Instagram linkini qisqartirish uchun hash funksiyasini ishlatish
            short_link = hashlib.md5(message.text.encode()).hexdigest()

            # Profil linkini saqlash
            await state.update_data(link=message.text)
            data = await state.get_data()

            # Tasdiqlash tugmasini yaratish
            btn = InlineKeyboardBuilder()
            btn.add(InlineKeyboardButton(text=data['name'], url=message.text))
            btn.button(
                text="✅ Tasdiqlash",
                callback_data=f"ikb8:{short_link}",  # Qisqartirilgan hashni callback_data'da ishlatish
            )
            btn.adjust(1, 1)

            await message.answer("Profilni tasdiqlaysizmi?", reply_markup=btn.as_markup())
            await state.set_state(AddInstagramProfile.check)
        except Exception as e:
            print(e)
            await message.answer("Yuborilgan havola noto'g'ri. Qaytadan yuboring!", reply_markup=back_button())

@dp.callback_query(CheckAddInstagramProfile.filter(), IsBotAdmin(), AddInstagramProfile.check)
async def confirm_instagram_profile(call: types.CallbackQuery, callback_data: CheckAddInstagramProfile, state: FSMContext):
    try:
        await call.answer("Instagram profil qo'shildi!", show_alert=True)

        # Holatdan ma'lumotlarni olish
        data = await state.get_data()
        name = data.get("name")
        link = callback_data.link

        # Instagram profilni ma'lumotlar bazasiga qo'shish
        await db.add_instagram_profile(
            name=name,
            link=link
        )

        # Admin paneliga qaytish
        await call.message.answer("👨‍💻 Admin panel!", reply_markup=admin_buttons())
        await call.message.delete()
        await state.clear()
    except Exception as e:
        print(e)