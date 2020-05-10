import random

from aiogram import types
from aiogram.types import Message
from aiogram.dispatcher.filters import Command, Text
from asyncpg import Connection, Record
from asyncpg.exceptions import UniqueViolationError
from keyboards import rps_menu, new_round_menu

from load_all import bot, dp, db


class DBCommands:
    pool: Connection = db
    ADD_NEW_USER = "INSERT INTO users(chat_id, username, full_name) VALUES ($1, $2, $3) RETURNING id"
    COUNT_USERS = "SELECT COUNT(*) FROM users"
    GET_ID = "SELECT id FROM users WHERE chat_id = $1"
    CHECK_LOSE = "SELECT count_loss FROM users WHERE chat_id = $1"
    CHECK_WIN = "SELECT count_win FROM users WHERE chat_id = $1"

    async def add_new_user(self):
        user = types.User.get_current()

        chat_id = user.id
        username = user.username
        full_name = user.full_name
        args = chat_id, username, full_name

        command = self.ADD_NEW_USER

        try:
            record_id = await self.pool.fetchval(command, *args)
            return record_id
        except UniqueViolationError:
            pass

    async def count_users(self):
        record: Record = await self.pool.fetchval(self.COUNT_USERS)
        return record

    async def get_id(self):
        command = self.GET_ID
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def check_lose(self):
        command = self.CHECK_LOSE
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)

    async def check_win(self):
        command = self.CHECK_WIN
        user_id = types.User.get_current().id
        return await self.pool.fetchval(command, user_id)


db = DBCommands()

player_score = 0
pc_score = 0
player_select = 0
pc_select = 0
round_number = 1


@dp.message_handler(Command("start"))
async def register_user(message: types.Message):
    chat_id = message.from_user.id
    id = await db.add_new_user()
    count_users = await db.count_users()

    text = ""
    if not id:
        id = await db.get_id()
    else:
        text += "Записал в базу! "

    win = await db.check_win()
    lose = await db.check_lose()
    text += f"""
    Сейчас в базе {count_users} человек!
    Ваш счёт: {win}:{lose}.
    """
    await bot.send_message(chat_id, text)


@dp.message_handler(Command('game'))
async def start_game(message: Message):
    await bot.send_message(message.from_user.id, "ROCK PAPER SCISSORS")
    await bot.send_message(message.from_user.id, "Start game!")
    await game(message)


@dp.message_handler(Text(equals='New round'))
async def other_text(message: Message):
    await game(message)


async def game(message: Message):
    names = ["rock", "paper", "scissors"]
    global player_score
    global pc_score
    global pc_select
    global round_number
    if pc_score < 3 and player_score < 3:
        pc_select = (names[random.randint(0, len(names)-1)])
        await bot.send_message(message.from_user.id, f"Round №{round_number}")
        round_number += 1
        await bot.send_message(message.from_user.id, "Your choice", reply_markup=rps_menu)
        await get_object(message)


async def get_object(message: Message):
    global player_select
    global pc_select
    global player_score
    global pc_score
    global round_number
    global game_value
    player_select = message.text.lower()
    if player_select != "rock" and player_select != "paper" and player_select != "scissors":
        player_select = "error"
    await bot.send_message(message.from_user.id, f"Your choice = {player_select}\nMy choice = {pc_select}")
    if player_select == "error":
        pc_score += 1
    elif (pc_select == "rock") and (player_select == "paper"):
        player_score += 1
    elif (pc_select == "rock") and (player_select == "scissors"):
        pc_score += 1
    elif (pc_select == "paper") and (player_select == "rock"):
        pc_score += 1
    elif (pc_select == "paper") and (player_select == "scissors"):
        player_score += 1
    elif (pc_select == "scissors") and (player_select == "paper"):
        pc_score += 1
    elif (pc_select == "scissors") and (player_select == "rock"):
        player_score += 1
    else:
        await bot.send_message(message.from_user.id, "Draw in this round")
    await bot.send_message(message.from_user.id, f"Current score: {player_score}:{pc_score}")
    if pc_score == 3:
        await bot.send_message(message.from_user.id, "Game over. I'm win, but I love you very much")
        await bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')
        pc_score = 0
        player_score = 0
        round_number = 1
        game_value = False
    elif player_score == 3:
        await bot.send_message(message.from_user.id, "Game over. You are win. I know that you are best and beautiful!!!")
        await bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')
        pc_score = 0
        player_score = 0
        round_number = 1
        game_value = False
    else:
        await bot.send_message(message.from_user.id, "Entering to new round", reply_markup=new_round_menu)

@dp.message_handler(Text)
async def other_text(message: Message):
    if message.text.lower() == "hi":
        await bot.send_message(message.from_user.id, "Hello! I am TestBot. How can i help you?")
    elif message.text.lower() == "how are you?":
        await bot.send_message(message.from_user.id, "Плохо. Скинь смешняфку")
    elif message.text.lower() == "love":
        await bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')
    elif message.text.lower() == "bye":
        await bot.send_message(message.from_user.id, "I don't love you((")
    else:
        await bot.send_message(message.from_user.id, "Sorry, i dont understand you.")


@dp.message_handler(content_types=['sticker'])
async def send_sticker(message: Message):
    await bot.send_message(message.from_user.id, "Смефно")
    print(message)


@dp.message_handler(content_types=['audio'])
async def send_sticker(message: Message):
    await bot.send_message(message.from_user.id, "Я тупой. Давай текст")
    print(message)
