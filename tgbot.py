from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import aiosqlite
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime

class authorization(StatesGroup):
    num = State()
    password = State()


TOKEN = ''
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot,storage=storage)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message,state: FSMContext):
    db = await aiosqlite.connect('database.db')
    cur = await db.cursor()
    user_check = await cur.execute('Select * from users where tg_id=?',(message.from_user.id,))
    user_check_row = await user_check.fetchall()
    logs = await cur.execute(f"Insert into tg_logs(user_id,action,time)values({message.from_user.id},'/start','{datetime.datetime.now()}')")
    await db.commit()
    if user_check_row == []:
        await message.reply("Введите табельный номер")
        await authorization.num.set()
        logs = await cur.execute(f"Insert into tg_logs(user_id,action,time)values({message.from_user.id},'Ввел табельный номер','{datetime.datetime.now()}')")
        await db.commit()
    else:
        work_markup= ReplyKeyboardMarkup(resize_keyboard=True)
        work_kb = work_markup.add('На работу')
        await message.reply("Вы уже авторизованы",reply_markup=work_kb)
        


@dp.message_handler(state=authorization.num)
async def num_check(message: types.Message, state: FSMContext) -> None:
    db = await aiosqlite.connect('database.db')
    cur = await db.cursor()
    async with state.proxy() as data:
        data['num'] = message.text
    await message.reply('А теперь пароль')
    await authorization.next()
    logs = await cur.execute(f"Insert into tg_logs(user_id,action,time)values({message.from_user.id},'Ввел пароль','{datetime.datetime.now()}')")
    await db.commit()


@dp.message_handler(state=authorization.password)
async def pwd_check(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['password'] = message.text
    db = await aiosqlite.connect('database.db')
    cur = await db.cursor()
    user = await cur.execute('Select * from users where num=? and password=?',(data['num'],data['password']))
    user_row = await user.fetchall()
    logs = await cur.execute(f"Insert into tg_logs(user_id,action,time)values({message.from_user.id},'Авторизовался','{datetime.datetime.now()}')")
    await db.commit()
    work_markup= ReplyKeyboardMarkup(resize_keyboard=True)
    work_kb = work_markup.add('На работу')

    await bot.send_message(message.from_user.id, f"Вы авторизовались как {user_row[0][2]}",reply_markup=work_kb)
    await cur.execute(f"UPDATE `users` SET `tg_id`='{message.from_user.id}' WHERE `num` = {user_row[0][1]}")
    await cur.execute(f"insert into tg_active(user_id,is_active)values({message.from_user.id},0)")
    await db.commit()
    await state.finish()


@dp.message_handler(text='На работу')
async def start_command(message: types.Message):
    db = await aiosqlite.connect('database.db')
    cur = await db.cursor()
    work_checksql = await cur.execute(f'Select * from users where tg_id={message.from_user.id}')
    work_check = await work_checksql.fetchall()
    if work_check ==[]:
         await bot.send_message(message.from_user.id,'Сначала авторизуйтесь')
    else:
        set_active = await cur.execute(f'Update tg_active set is_active=1 where user_id={message.from_user.id}')
        await cur.execute(f"Insert into tg_logs(user_id,action,time)values({message.from_user.id},'Стал активен','{datetime.datetime.now()}')")
        user_role_check = await cur.execute(f'Select role from users where tg_id={message.from_user.id}')
        user_role = await user_role_check.fetchall()
        await db.commit()
        unactive_markup= ReplyKeyboardMarkup(resize_keyboard=True)
        unactive_kb = unactive_markup.add('Я все')
        if user_role[0][0] == 1:
            await bot.send_message(message.from_user.id,'Теперь вы активны как диспетчер',reply_markup=unactive_kb)
            @dp.message_handler()
            async def start_command(message: types.Message):
                db = await aiosqlite.connect('database.db')
                cur = await db.cursor()
                client_idsql = await cur.execute('Select tg_id from users where role=0')
                client_id = await client_idsql.fetchall()
                client_activesql = await cur.execute(f'Select is_active from tg_active where user_id={client_id[0][0]}')
                client_active = await client_activesql.fetchall()
                if client_active[0][0] == 1:
                    await bot.send_message(client_id[0][0],message.text)
                else:
                     await bot.send_message(message.from_user.id,"Никого нет в сети")
        else:
            await bot.send_message(message.from_user.id,'Теперь вы активны',reply_markup=unactive_kb)


@dp.message_handler(text='Я все')
async def start_command(message: types.Message):
    db = await aiosqlite.connect('database.db')
    cur = await db.cursor()
    set_unactive = await cur.execute(f'Update tg_active set is_active=0 where user_id={message.from_user.id}')
    await cur.execute(f"Insert into tg_logs(user_id,action,time)values({message.from_user.id},'Перестал быть активен','{datetime.datetime.now()}')")
    await db.commit()
    work_markup= ReplyKeyboardMarkup(resize_keyboard=True)
    work_kb = work_markup.add('На работу')
    await bot.send_message(message.from_user.id,'Вы больше не активны',reply_markup=work_kb)






if __name__ == '__main__':
    executor.start_polling(dp)