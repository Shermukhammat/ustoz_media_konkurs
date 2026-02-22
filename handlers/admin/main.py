from loader import db, dp, bot
from aiogram import Router, types, F 
from aiogram.filters import Command
from asyncio import Semaphore
from states import AdminPanel
from aiogram.fsm.context import FSMContext
from buttons import KeyboardButtons, InlineButtons
from utils import can_edit
from db import User
from asyncio import sleep
import pandas as pd


ADMIN_COMMANDS = [
    types.BotCommand(command="admin", description="👨🏻‍💻 Admin panel"),
    types.BotCommand(command="id", description="🆔 ni olish")
]

async def set_admin_commands(user_id: int):
    """Give a user the /admin command visible only in their private chat."""
    await bot.set_my_commands(
        commands=ADMIN_COMMANDS,
        scope=types.BotCommandScopeChat(chat_id=user_id)
    )

async def remove_admin_commands(user_id: int):
    """Remove the /admin command from a user's private chat."""
    await bot.delete_my_commands(
        scope=types.BotCommandScopeChat(chat_id=user_id)
    )


r = Router(name='admin')
dp.include_router(r)


@r.message(Command('admin'))
async def show_admin_panel(update: types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if user and user.id == db.dev_id:
        user.is_admin = True
        await db.update_user(id = user.id, is_admin = True)

    if user and user.is_admin:
        await state.set_state(AdminPanel.main)
        await update.answer("👨🏻‍💻 Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)


@r.message(Command('update_commands'))
async def update_commands(update: types.Message):
    user = await db.get_user(update.from_user.id)
    if not (user and (user.is_admin or user.id == db.dev_id)):
        return

    admins = await db.get_admins()
    updated = 0
    for admin in admins:
        try:
            await set_admin_commands(admin.id)
            updated += 1
        except Exception:
            pass  # skip if admin blocked the bot

    await update.answer(f"✅ {updated} ta admin uchun buyruqlar yangilandi.")


@r.message(Command('id'))
async def show_id(update: types.Message):
    await update.reply(f"`{update.from_user.id}`", parse_mode='markdown')


@r.channel_post(Command('id'))
async def show_chanel_id(update: types.Message):
    msg = await update.reply(f"`{update.chat.id}`", parse_mode='markdown')
    
    await sleep(3)
    await msg.delete()
    await update.delete()



@r.message(AdminPanel.main)
async def admin_panel_main(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Chiqish":
        await state.clear()
        await update.answer("Admin paneldan chiqdingiz", reply_markup=KeyboardButtons.HOME)
    
    elif update.text == "📊 Statistika":
        info = await db.get_statistic()
        await update.answer(f"🟢 Aktiv foydlanuvchilar: {info.activ_users} \n🚶 Tark etganlar: {info.lived_users}  \n➕ Bugun {info.today_joined} ta foydalanuchi qo'shildi \n➕ Bu hafta {info.week_joined} ta foydalanuchi qo'shildi \n➕ Bu oy {info.month_joined} ta foydalanuchi qo'shildi \n🔥 Bugun botdan {info.dayly_users} ta odam foydalandi",
                            reply_markup = KeyboardButtons.ADMIN_PANEL)
    
    elif update.text == "👨🏻‍💻 Adminlar":
        text = "📑 Adminlar: \n"
        for index, admin in enumerate(await db.get_admins()):
            text += f"\n{index+1}. {admin.full_name} \n🆔: <code>{admin.id}</code>"
        await update.answer(text, parse_mode='HTML', reply_markup=InlineButtons.ADMINS_BUTTON)

    elif update.text == "⬇️ Foydlanuvchilar excel":
        await send_users_doc(update)
    
    elif update.text == "🚀 Xabar yuborish":
        await state.set_state(AdminPanel.get_ads_media)
        await update.answer("1ta mediadan tashkil topgan xabaringizni yuboring. Rasm, video, fayl, video yoki audio xabar. Agar foydlnuvchi ismni postga qoymoqchi bolsanigz {name} deb yozing", 
                            reply_markup=KeyboardButtons.back())

    elif update.text == "⚙️ Sozlamalar":
        await state.set_state(AdminPanel.settings)
        await update.answer("Sozlamalar bo'limi", reply_markup=KeyboardButtons.SETTINGS)
    
    else:
        await update.answer("👨🏻‍💻 Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)
    


from asyncio import Semaphore 
import os 


sema = Semaphore()
os.makedirs('files/tmp', exist_ok=True)

async def send_users_doc(update: types.Message):
    async with sema:
        df = pd.DataFrame([{'Id': user.id, 
                            'I.F': user.full_name,
                            "No'mer" : user.phone_number,
                            "Username": user.username,
                            "Taklif qildi": user.invited_users,
                            "Ro'yxatdan o'tdi": user.registred_readble,
                            } for user in await db.get_useres()])
        
        df.to_excel('files/tmp/users.xlsx', index=False)

    await bot.send_chat_action(chat_id=update.chat.id, action='upload_document')
    await sleep(2)
    await bot.send_document(chat_id=update.chat.id, document=types.FSInputFile('files/tmp/users.xlsx'))



@r.callback_query(F.data == 'add_admin')
async def add_admin(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.add_admin)
    await update.message.answer("Admin qilmoqchi bo'lgan foydalanuvchin idsnini yuboring. Idni /id commandasi bilan olish mumkun",
                        reply_markup=KeyboardButtons.back()) 


@r.callback_query(F.data == 'remove_admin')
async def remove_admin(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminPanel.remove_admin)
    await update.message.answer("Olib tashlamoqchi bo'lgan admin idsnini yuboring. Idni /id commandasi bilan olish mumkun",
                        reply_markup=KeyboardButtons.back()) 

@r.message(AdminPanel.add_admin, F.text)
async def creare_admin(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.main)
        await update.answer("Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)
    
    elif update.text.isnumeric():
        if int(update.text) == update.from_user.id:
            await update.answer("❗️ Siz allaqochon adminsiz", reply_markup=KeyboardButtons.back())
            return
        user = await db.get_user(int(update.text))
        if user:
            await db.update_user(id = user.id, is_admin = True)
            await set_admin_commands(user.id)
            await state.set_state(AdminPanel.main)
            await update.answer("✅ Admin qo'shildi", reply_markup=KeyboardButtons.ADMIN_PANEL)

        else:
            await update.reply("❗️ Bunday foydalanuvchi topilmadi", reply_markup=KeyboardButtons.back())

    else:
        await update.reply("❗️ Iltimos idni to'g'ri kiriting", reply_markup=KeyboardButtons.back())



@r.message(AdminPanel.remove_admin, F.text)
async def remove_admin(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.main)
        await update.answer("Admin panel", reply_markup=KeyboardButtons.ADMIN_PANEL)

    elif update.text.isnumeric():
        user = await db.get_user(int(update.text))

        if user and user.is_admin:        
            if user.id == update.from_user.id:
                await update.answer("😁 O'zingizni o'chira olmaysiz", reply_markup=KeyboardButtons.back())
            else:
                await state.set_state(AdminPanel.main)
                await db.update_user(id = user.id, is_admin = False)
                await remove_admin_commands(user.id)
                await update.answer("✅ Admin o'chirildi", reply_markup=KeyboardButtons.ADMIN_PANEL)
        else:
            await update.reply("❗️ Bunday admin topilmadi", reply_markup=KeyboardButtons.back())
    else:
        await update.reply("❗️ Iltimos idni to'g'ri kiriting", reply_markup=KeyboardButtons.back())


# @r.message(F.sticker)
# async def sticker(update: types.Message):
#     print(update.sticker.file_id)

