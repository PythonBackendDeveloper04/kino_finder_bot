from loader import dp, db
from filters import IsPrivate,IsBotAdmin
from aiogram import types,F
from aiogram.fsm.context import FSMContext
from states.states import AddMovie

@dp.message(F.text=="🎞 Kino qo'shish",IsPrivate(),IsBotAdmin())
async def add_movie(message:types.Message,state:FSMContext):
    await message.answer("Post ID kiriting")
    await state.set_state(AddMovie.post_id)
@dp.message(F.text,AddMovie.post_id)
async def get_post_id(message:types.Message,state:FSMContext):
    post_id = message.text
    await state.update_data({
        "post_id":post_id
    })

    await message.answer("Kino kodini kiriting")
    await state.set_state(AddMovie.code)
@dp.message(F.text, AddMovie.code)
async def get_code(message: types.Message, state: FSMContext):
    code = message.text
    await state.update_data({
        "code": code
    })

    data = await state.get_data()
    try:
        await db.add_movie(post_id=data['post_id'],code=data['code'])
        await message.answer("Movie added")
        await state.clear()
    except Exception as e:
        await message.answer("Bu kodli kino mavjud")