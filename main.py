import asyncio
import os
import aiogram
import sqlite3
import config
import random
from matplotlib import pyplot as plt
import json
import datetime
from colorama import Fore, init
bot = aiogram.bot.Bot(config.BOT_TOKEN, )
dp = aiogram.Dispatcher(bot)
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Список карт
cards = os.listdir('Cards')

# Выбор рандомных кард
def get_random_cards(pack_size):
    random_cards = []
    for x in range(pack_size):
        random_card = random.choice(cards)
        random_cards.append(random_card)
    return random_cards

def is_new_user(user_id):
    """Проверка новый ли пользователь"""
    cursor.execute("SELECT * FROM data WHERE id=?", (user_id,))
    data = cursor.fetchone()
    if data is None:
        return True
    else:
        return False

def get_all_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM data")
    rows = cursor.fetchall()

    users = []
    for row in rows:
        users.append(str(row[0]))

    return users

async def check_subscription(user_id):
    channel = await bot.get_chat(config.CHANNEL_ID)
    channel_name = channel.full_name
    channel_username = channel.username
    user = await bot.get_chat_member(chat_id=config.CHANNEL_ID, user_id=user_id)
    if not user.status in config.STATUSES:
        await bot.send_message(user_id, 'Привет Для доступа к боту ты должен подписаться на наш канал\nПосле подписки напиши /start', reply_markup=aiogram.types.InlineKeyboardMarkup(row_width=1).add(aiogram.types.InlineKeyboardButton(text=channel_name, url=f'https://t.me/{channel_username}')))
        return True
    else:
        return False

async def init_bot(dp: aiogram.Dispatcher):
    commands = [aiogram.types.BotCommand('/start', 'Профиль'),
            aiogram.types.BotCommand('/help', 'Помощь'),
            aiogram.types.BotCommand('/info', 'Информация о боте'),
            aiogram.types.BotCommand('/play', 'Играть в матчи (стоимость игры: 5000 монет)'),
            aiogram.types.BotCommand('/packs', 'Меню с паками'),
            aiogram.types.BotCommand('/change_info', 'Изменить информацию'),
            aiogram.types.BotCommand('/change_avatar', 'Изменить аватар профиля'),
            aiogram.types.BotCommand('/leaderboard', 'Таблица лидеров')]
    await dp.bot.set_my_commands(commands=commands)

@dp.message_handler(commands=['send'])
async def send_resources(message: aiogram.types.Message):
    if str(message.from_user.id) in config.ADMINS:
        count = 0
        users = get_all_users()
        text = "Отчёт о отппраке монет:\n"
        for user_id in users:
            cursor.execute("SELECT coins, free_packs FROM data WHERE id=?", (user_id,))
            data = cursor.fetchone()
            cursor.execute("UPDATE data SET coins=?, free_packs=? WHERE id=?", (data[0] + 10000, 1, user_id))
            conn.commit()
            try:
                await bot.send_message(user_id, '💰 Вам начислено 10.000 монет.')
                print(Fore.GREEN + f'Успешно отправлено к пользователю {str(user_id)}')
                text += f'Успешно отправлено к пользователю {str(user_id)}'
                count += 1
            except Exception as exception:
                print(Fore.RED + f'Ошибка отправления сообщения к пользователю {str(user_id)}\n'
                                 f'Причина ошибки: {exception}')
                text += f'Ошибка отправления сообщения к пользователю {str(user_id)}\nПричина ошибки: {exception}'
        print(Fore.CYAN + f'Успешно отправлено {count} пользователям из {len(users)}\nВсего отправлено {count * 7500} монет из {len(users) * 7500}')
        text += f'Успешно отправлено {count} пользователям из {len(users)}\nВсего отправлено {count * 7500} монет из {len(users) * 7500}'
        await bot.send_message(message.from_user.id, text)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: aiogram.types.Message):
    print(f'Go to profile: {message.from_user.id}')
    player_id = message.from_user.id
    msg = await bot.send_message(player_id, 'Удаление кнопок', reply_markup=aiogram.types.ReplyKeyboardRemove())
    await bot.delete_message(player_id, msg.message_id)
    channel = await bot.get_chat(config.CHANNEL_ID)
    channel_name = channel.full_name
    channel_username = channel.username
    if await check_subscription(player_id):
        return
    if is_new_user(player_id):
        cursor.execute("INSERT INTO data (id, coins, opened_packs, cards, info) VALUES (?, 25000, 0, 0, ?)", (player_id, None))
        conn.commit()
        await bot.send_message(player_id, f'Привет Представляем вам бота специально от [{channel_name}](https://t.me/{channel_username})\nБот создан исключительно в развлекательных целях и не имеет никаких платных функций (кроме покупки предметов за виртуальные ресурсы)\nНаслаждайтесь', parse_mode=aiogram.types.ParseMode.MARKDOWN_V2)
    cursor.execute("SELECT coins, opened_packs, cards, info FROM data WHERE id=?", (player_id,))
    try:
        data = cursor.fetchone()
        coins = data[0]
        opened_packs = data[1]
        cards = len(str(data[2]).split()) if len(str(data[2]).split()) > 1 else 0
        info = data[3] if data[3] is not None else "Информация не указана"
    except:
        await bot.send_message(player_id, 'Вы не зарегистрированы в игре')
    try:
        with open(f'users_data/avatar_u{player_id}.png', 'rb') as f:
            await bot.send_photo(chat_id=player_id, photo=f, caption=f'Привет Твой профиль:\n\nИнформация:\n{info}\n💰 Монет - {coins}\n📦 Открыто Паков - {opened_packs}\n🌐 Карт - {cards}')
    except FileNotFoundError:
        with open(f'users_data/avatar_is_none.png', 'rb') as f:
            await bot.send_photo(chat_id=player_id, photo=f, caption=f'Привет Твой профиль:\n\nИнформация:\n{info}\n💰 Монет - {coins}\n📦 Открыто Паков - {opened_packs}\n🌐 Карт - {cards}')

@dp.message_handler(commands=['change_info'])
async def process_callback_change_info(message):
    await bot.send_message(message.from_user.id, 'Введите новую информацию о себе')
    dp.register_message_handler(process_new_info, content_types=aiogram.types.ContentTypes.TEXT)
async def process_new_info(message: aiogram.types.Message):
    user_id = str(message.from_user.id)
    new_info = str(message.text)
    if len(new_info) > 15:
        await bot.send_message(user_id, 'Информация не может быть длиннее 15 символов')
        return
    try:
        cursor.execute("UPDATE data SET info=? WHERE id=?", (new_info, user_id))
    except:
        await bot.send_message(user_id, 'Вы не зарегистрированы в игре')
    conn.commit()
    dp.message_handlers.unregister(process_new_info)
    await bot.send_message(user_id, 'Информация успешно сохранена\n'
                                    'Чтобы её увидить напишите /start')
@dp.message_handler(commands=['change_avatar'])
async def process_change_avatar(message):
    if await check_subscription(message.from_user.id):
        return
    user_id = str(message.from_user.id)
    await bot.send_message(user_id, 'Отлично! Теперь пришли мне свой новый аватар (только фото!!!)')
    dp.register_message_handler(process_new_avatar, content_types=aiogram.types.ContentTypes.PHOTO)
async def process_new_avatar(message: aiogram.types.Message):
    user_id = str(message.from_user.id)
    photo = message.photo[-1]
    photo_path = f"users_data/avatar_u{user_id}.png"

    await photo.download(photo_path)
    if os.path.isfile(photo_path):
        await bot.send_message(user_id, 'Отлично! Аватар успешно обновлен. Чтобы его увидеть напишите /start')
    else:
        await bot.send_message(user_id, 'Упс! Что-то пошло не так. Попробуйте еще раз.')
    dp.message_handlers.unregister(process_new_avatar)
@dp.message_handler(commands=['play'])
async def play_match(message: aiogram.types.Message):
    print(f'Play menu: {message.from_user.id}')
    if await check_subscription(message.from_user.id):
        return
    play_markup = aiogram.types.InlineKeyboardMarkup(row_width=1).add(aiogram.types.InlineKeyboardButton(text='⚽ Играть ⚽', callback_data='start_play'))
    await bot.send_message(message.from_user.id, 'Стоимость одной игры в матч: 5000 монет\nЧтобы подтвердить игру нажмите кнопку внизу (с помощью данной кнопки вы можете играть не набирая команду /play ещё раз)', reply_markup=play_markup)

@dp.callback_query_handler(lambda c: c.data == 'start_play')
async def start_play(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, 'Начало матча')
    print(f'Playing match: {callback_query.from_user.id}')
    if await check_subscription(callback_query.from_user.id):
        return
    player_id = callback_query.from_user.id
    cursor.execute("SELECT coins FROM data WHERE id=?", (player_id,))
    try:
        player_coins = cursor.fetchone()[0]
    except TypeError:
        await bot.send_message(player_id, 'Вы не зарегистрированы в игре')
    if player_coins >= 5000:
        cursor.execute("UPDATE data SET coins=coins-5000 WHERE id=?", (player_id,))
        conn.commit()
        cursor.execute("SELECT info, id FROM data WHERE id != ? ORDER BY RANDOM() LIMIT 1", (player_id,))
        opponent_name, opponent_id = cursor.fetchone()
        player_score = random.randint(0, 7)
        opponent_score = random.randint(0, 7)
        await bot.send_message(callback_query.from_user.id, f"Игра началась\nВаш противник: {opponent_name if opponent_name == 'None' else f'Игрок {opponent_id}'}")
        await asyncio.sleep(6)
        if player_score > opponent_score:
            cursor.execute("UPDATE data SET coins=coins+10000 WHERE id=?", (player_id,))
            conn.commit()
            await bot.send_message(callback_query.from_user.id, f"✅ - Вы победили со счётом {player_score}:{opponent_score}\nВы получили 10000 монет")
        elif player_score < opponent_score:
            await bot.send_message(callback_query.from_user.id, f"❌ - Вы проиграли со счётом {player_score}:{opponent_score}")
        elif player_score == opponent_score:
            await bot.send_message(callback_query.from_user.id, f"🟨 - Вы сыграли вничью со счётом {player_score}:{opponent_score}")
    else:
        await bot.send_message(callback_query.from_user.id, "У вас недостаточно монет для начала игры\nНужно 5000")
        return

def update_json_batabase():
    """Обновляет базу данных и ничего не возвращает"""
    cursor.execute('SELECT id, info, coins FROM data')
    rows = cursor.fetchall()

    # Создание словаря с данными
    users = {}
    for row in rows:
        users[str(row[0])] = {
            "info": row[1] if not row[0] == 'None' or not row[0] == None or not row[0] == '' else f"Игрок {str(row[0])}",
            "coins": row[2]
        }

    # Сохранение данных в файл JSON
    with open('users.json', 'w+') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

@dp.message_handler(commands=['leaderboard'])
async def get_leaderboard(call: aiogram.types.Message):
    if await check_subscription(call.from_user.id):
        return
    user_id = str(call.from_user.id)
    msg = await bot.send_message(call.from_user.id, 'Подождите, таблица лидеров загружаеться...')
    update_json_batabase()
    with open('users.json', 'r', encoding='utf-8') as f:
        players_data = json.load(f)
    players = [
        {"id": player_id, "name": player_data["info"] if not player_data['info'] == None else f"Игрок {player_id}", "success_rate": player_data['coins']}
        for player_id, player_data in players_data.items()]
    sorted_players = sorted(players, key=lambda x: x["success_rate"], reverse=True)[:10]
    fig, ax = plt.subplots()
    table_data = [["Номер", "Информация", "Монеты"]]

    for i, player in enumerate(sorted_players):
        table_data.append([i + 1, player["name"], round(player["success_rate"])])
    user_in_top_10 = False
    for i, player in enumerate(sorted_players):
        if player['id'] == str(call.from_user.id):
            user_in_top_10 = True
            break
    if not user_in_top_10:
        for i, player in enumerate(players):
            if player['id'] == str(call.from_user.id):
                table_data.append([i + 1, player["name"], round(player["success_rate"])])
                break
    table = ax.table(cellText=table_data, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(4)
    table.scale(1, 4)
    ax.axis('off')
    img = plt.imread('background.jpg')
    ax.imshow(img, extent=[0.0, 1.0, 0.0, 1.0], aspect='auto', alpha=0.3)
    fig.patch.set_facecolor('black')
    for cell in table.properties()['children']:
        cell.set_facecolor('white')
    channel = await bot.get_chat(config.CHANNEL_ID)
    channel_name = channel.full_name
    title = ax.set_title(f"Таблица лидеров бота от {channel_name}", fontsize=18)
    title.set_color('white')
    cell_dict = table.get_celld()
    for i in range(len(table_data)):
        for j in range(len(table_data[0])):
            cell_dict[(i, j)].set_width(0.25)
            cell_dict[(i, j)].set_text_props(weight='bold')
            if i == 0:
                cell_dict[(i, j)].set_height(0.1)
            else:
                cell_dict[(i, j)].set_height(0.075)
    for i, player in enumerate(sorted_players):
        if player['id'] == str(call.from_user.id):
            user_in_top_10 = True
            if i < 11:
                for j in range(len(table_data[0])):
                    cell_dict[(i + 1, j)].set_text_props(weight='bold', fontsize=5)
                    cell_dict[(i + 1, j)].set_facecolor('lightblue')
                    cell_dict[(i + 1, j)].set_edgecolor('blue')
                    cell_dict[(i + 1, j)].set_linewidth(1.5)

            break
    if not user_in_top_10:
        for i, player in enumerate(players):
            if player['id'] == str(call.from_user.id):
                row_index = len(table_data) - 1
                for j in range(len(table_data[0])):
                    cell_dict[(row_index, j)].set_text_props(weight='bold', fontsize=5)
                    cell_dict[(row_index, j)].set_facecolor('lightblue')
                    cell_dict[(row_index, j)].set_edgecolor('blue')
                    cell_dict[(row_index, j)].set_linewidth(1.5)
                break

    now = datetime.datetime.now()
    formatted_date = now.strftime("%d-%m-%y_%H-%M")
    plt.savefig(f'leaderboards/{formatted_date}_u{call.from_user.id}.png', dpi=750)

    await bot.delete_message(chat_id=user_id, message_id=msg.message_id)
    with open(f'leaderboards/{formatted_date}_u{call.from_user.id}.png', 'rb') as photo:
        await bot.send_photo(chat_id=call.from_user.id, photo=photo, caption='Таблица лидеров на данный момент')
    os.remove(f'leaderboards/{formatted_date}_u{call.from_user.id}.png')

@dp.message_handler(commands=['info'])
async def get_info(message):
    print(f'Getting info: {message.from_user.id}')
    if await check_subscription(message.from_user.id):
        return
    channel = await bot.get_chat(config.CHANNEL_ID)
    channel_name = channel.full_name
    channel_username = channel.username
    players = len(cursor.execute("SELECT * FROM data").fetchall())
    response = f'Информация о боте от <a href="https://t.me/{channel_username}">{channel_name}</a>\nПользователей: {players}\nАвтор: {config.ADMIN_NICKNAME}\nДля связи: {str(", ").join(config.SUPPORT)}'
    await bot.send_message(message.from_user.id, response, parse_mode=aiogram.types.ParseMode.HTML)

@dp.message_handler(commands=['packs'])
async def packs_menu(message):
    print(f'Packs menu: {message.from_user.id}')
    if await check_subscription(message.from_user.id):
        return
    data = cursor.execute("SELECT coins, free_packs FROM data WHERE id=?", (message.from_user.id,)).fetchone()
    await bot.send_message(message.from_user.id, '''Паки:

В день вам даётся пак 85+

Золотой премиум набор:
3 игрока 5.000 монет

Большой золотой набор:
7 игроков 10.000 монет

Редкий набор игроков:
15 игроков 15.000 монет

Большой Набор игроков:
20 игроков 26.000 монет

Набор ультимейт:
50.000 монет = 35 игроков''', reply_markup=aiogram.types.InlineKeyboardMarkup(row_width=1).add(
        aiogram.types.InlineKeyboardButton(text=f'Бесплатный пак ({data[1]} осталось)', callback_data='free_pack'),
          aiogram.types.InlineKeyboardButton(text='Золотой премиум набор', callback_data='gold_pack'),
            aiogram.types.InlineKeyboardButton(text='Большой золотой набор', callback_data='big_gold_pack'),
              aiogram.types.InlineKeyboardButton(text='Редкий набор игроков', callback_data='rare_pack'),
                aiogram.types.InlineKeyboardButton(text='Большой Набор игроков', callback_data='big_pack'),
                aiogram.types.InlineKeyboardButton(text='Набор ультимейт', callback_data='ultimate_pack')))

@dp.callback_query_handler(lambda c: c.data in ['free_pack', 'gold_pack', 'big_gold_pack', 'rare_pack', 'big_pack', 'ultimate_pack'])
async def process_buy_pack(callback_query: aiogram.types.CallbackQuery):
    print(f'Opening pack: {callback_query.from_user.id}')
    if await check_subscription(callback_query.from_user.id):
        return
    
    response = ""
    user_id = callback_query.from_user.id
    data = cursor.execute("SELECT coins, free_packs FROM data WHERE id=?", (user_id,)).fetchone()
    pack_cost = 0
    pack_size = 0
    is_free_pack = False
    if callback_query.data == 'free_pack':
        pack_size = 1
        if data[1] <= 0:
            await bot.send_message(user_id, 'У вас закончились бесплатные паки, приходите завтра')
            return
        is_free_pack = True
    elif callback_query.data == 'gold_pack':
        pack_cost = 5000
        pack_size = 3
    elif callback_query.data == 'big_gold_pack':
        pack_cost = 10000
        pack_size = 7
    elif callback_query.data == 'rare_pack':
        pack_cost = 15000
        pack_size = 15
    elif callback_query.data == 'big_pack':
        pack_cost = 20000
        pack_size = 20
    elif callback_query.data == 'ultimate_pack':
        pack_cost = 50000
        pack_size = 35

    msg = await bot.send_message(user_id, 'Проверяем данные...')
    await bot.delete_message(user_id, message_id=msg.message_id)
    if int(data[0]) < pack_cost:
        response = f'Вам не хватает монет для открытия пака\nНужно {pack_cost}'
    else:
        if is_free_pack:
            cursor.execute("UPDATE data SET free_packs=? WHERE id=?", (0, user_id))
        else:
            cursor.execute("UPDATE data SET coins=? WHERE id=?", (data[0] - pack_cost, user_id))
        conn.commit()
        cards = get_random_cards(pack_size)
        for card in cards:
            with open(f'Cards/{card}', 'rb') as current_card:
                await bot.send_document(user_id, document=current_card, caption='Вы получили игрока')
                await asyncio.sleep(0.1)

if __name__ == '__main__':
    aiogram.executor.start_polling(dp, on_startup=init_bot)

