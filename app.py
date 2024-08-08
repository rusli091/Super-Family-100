import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
from dotenv import load_dotenv
from questions import get_random_question, check_answer
from database import Database
from rate_limiter import RateLimiter

# Load environment variables
load_dotenv()

# Get environment variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

# Check and warn if environment variables are missing
missing_vars = []
if not API_ID:
    missing_vars.append("API_ID")
if not API_HASH:
    missing_vars.append("API_HASH")
if not BOT_TOKEN:
    missing_vars.append("BOT_TOKEN")
if not OWNER_ID:
    missing_vars.append("OWNER_ID")

if missing_vars:
    for var in missing_vars:
        logging.warning(f"Environment variable {var} is missing. Please check your .env file.")

# Use default values if variables are missing (just for this example, replace with actual handling)
API_ID = int(API_ID) if API_ID else 123456
API_HASH = API_HASH if API_HASH else "default_api_hash"
BOT_TOKEN = BOT_TOKEN if BOT_TOKEN else "default_bot_token"
OWNER_ID = int(OWNER_ID) if OWNER_ID else 12345678

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SuperFamily100Bot:
    def __init__(self):
        self.app = Client("super_family_100_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        self.user_scores = {}
        self.group_scores = {}
        self.blacklisted_users = set()
        self.blacklisted_groups = set()
        self.group_in_game = set()
        self.game_timers = {}
        self.current_questions = {}
        self.user_in_game = {}
        self.registered_chats = set()  # Track registered chats for broadcasting

        self.locks = {
            'user_scores': asyncio.Lock(),
            'group_scores': asyncio.Lock(),
            'current_questions': asyncio.Lock(),
            'game_timers': asyncio.Lock(),
            'user_in_game': asyncio.Lock(),
            'registered_chats': asyncio.Lock()  # Lock for registered chats
        }

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(rate_limit=5, time_window=60)  # 5 requests per minute

        # Add handlers
        self.app.add_handler(MessageHandler(self.start, filters.command("start")))
        self.app.add_handler(MessageHandler(self.bantuan, filters.command("help")))
        self.app.add_handler(MessageHandler(self.mulai, filters.command("mulai")))
        self.app.add_handler(MessageHandler(self.nyerah, filters.command("nyerah")))
        self.app.add_handler(MessageHandler(self.next, filters.command("next")))
        self.app.add_handler(MessageHandler(self.stats, filters.command("stats")))
        self.app.add_handler(MessageHandler(self.top, filters.command("top")))
        self.app.add_handler(MessageHandler(self.topgrup, filters.command("topgrup")))
        self.app.add_handler(MessageHandler(self.peraturan, filters.command("peraturan")))
        self.app.add_handler(MessageHandler(self.blacklist, filters.command("blacklist")))
        self.app.add_handler(MessageHandler(self.whitelist, filters.command("whitelist")))
        self.app.add_handler(MessageHandler(self.broadcast, filters.command("broadcast") & filters.user(OWNER_ID)))
        self.app.add_handler(MessageHandler(self.handle_answer, filters.text & filters.group))

    async def rate_limited(self, user_id):
        if self.rate_limiter.is_rate_limited(user_id):
            await self.app.send_message(user_id, "Anda terlalu sering menggunakan perintah ini. Silakan coba lagi nanti.")
            return True
        return False

    async def start(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        user_fullname = message.from_user.first_name
        user_id = message.from_user.id

        async with self.locks['registered_chats']:
            self.registered_chats.add(message.chat.id)  # Register chat for broadcasting

        if message.reply_to_message and message.reply_to_message.from_user.is_bot:
            await self.start_game(client, message)
        else:
            welcome_text = (
                f"Halo {user_fullname}, ayo kita main Super Family 100.\n"
                "/mulai : mulai game\n"
                "/nyerah : menyerah dari game\n"
                "/next : Pertanyaan berikutnya\n"
                "/help : membuka pesan bantuan\n"
                "/stats : melihat statistik kamu\n"
                "/top : lihat top skor global\n"
                "/topgrup : lihat top skor grup\n"
                "/peraturan : aturan bermain"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Invite ke group +", url="https://t.me/Pintar100_bot")]
            ])
            await message.reply_text(welcome_text, reply_markup=keyboard)

    async def bantuan(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        await message.reply_text(
            "/mulai : mulai game\n"
            "/nyerah : menyerah dari game\n"
            "/next : Pertanyaan berikutnya\n"
            "/help : membuka pesan bantuan\n"
            "/stats : melihat statistik kamu\n"
            "/top : lihat top skor global\n"
            "/topgrup : lihat top skor grup\n"
            "/peraturan : aturan bermain\n"
        )

    async def mulai(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        if message.from_user.id in self.blacklisted_users or message.chat.id in self.blacklisted_groups:
            await message.reply_text("Anda atau grup ini telah diblokir dari permainan.")
            return

        await self.start_game(client, message)

    async def start_game(self, client, message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        async with self.locks['user_in_game']:
            if chat_id not in self.user_in_game:
                self.user_in_game[chat_id] = set()
            self.user_in_game[chat_id].add(user_id)

        question, answers = get_random_question()
        correct_answers = ["_" * len(ans) for ans, _ in answers]
        answerers = [[] for _ in answers]

        async with self.locks['current_questions']:
            if chat_id not in self.current_questions:
                self.current_questions[chat_id] = {}
            self.current_questions[chat_id][user_id] = {
                "question": question,
                "answers": answers,
                "correct_answers": correct_answers,
                "answerers": answerers
            }

        formatted_question = self.format_question(question, correct_answers, answerers)
        await message.reply_text(formatted_question)

        async with self.locks['group_in_game']:
            self.group_in_game.add(chat_id)

        async with self.locks['game_timers']:
            if chat_id not in self.game_timers:
                self.game_timers[chat_id] = {}
            self.game_timers[chat_id][user_id] = asyncio.get_running_loop().call_later(60, self.next_game_question, client, chat_id, user_id)

        db = Database('family100.db')
        db.update_score(chat_id, message.from_user.username, 0)
        db.close()

    async def next_game_question(self, client, chat_id, user_id):
        await client.send_message(chat_id, f"/next {user_id}")

    async def handle_answer(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.from_user.username

        async with self.locks['current_questions']:
            if chat_id not in self.current_questions:
                return

            user_answer = message.text.strip().lower()
            for uid in list(self.current_questions[chat_id].keys()):
                current_question = self.current_questions[chat_id][uid]
                question = current_question["question"]
                correct_answers = current_question["correct_answers"]
                all_answers = current_question["answers"]
                answerers = current_question["answerers"]

                if check_answer(user_answer, all_answers):
                    for i, (answer, points) in enumerate(all_answers):
                        if answer.lower() == user_answer:
                            correct_answers[i] = answer
                            answerers[i].append(user_name)
                            break

                    await message.reply_text(
                        f"✅ Jawaban benar: {user_answer} ({points} poin) - {user_name}"
                    )

                    formatted_question = self.format_question(question, correct_answers, answerers)
                    await message.reply_text(formatted_question)

                    db = Database('family100.db')
                    db.update_score(chat_id, user_name, points)
                    db.close()

                    if all("_" not in ans for ans in correct_answers):
                        await message.reply_text("Semua jawaban sudah ditemukan. Gunakan /next untuk pertanyaan berikutnya.")
                        del self.current_questions[chat_id][uid]

                        async with self.locks['user_in_game']:
                            self.user_in_game[chat_id].discard(uid)

                        async with self.locks['game_timers']:
                            if chat_id in self.game_timers and uid in self.game_timers[chat_id]:
                                self.game_timers[chat_id][uid].cancel()
                                del self.game_timers[chat_id][uid]

                    break

    async def nyerah(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        async with self.locks['user_in_game']:
            if chat_id in self.user_in_game and user_id in self.user_in_game[chat_id]:
                self.user_in_game[chat_id].discard(user_id)
                await message.reply_text(f"Pengguna {message.from_user.first_name} telah menyerah.")
            else:
                await message.reply_text("Anda belum memulai permainan.")

    async def next(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        if len(message.command) > 1:
            try:
                user_id = int(message.command[1])
            except ValueError:
                await message.reply_text("ID pengguna tidak valid.")
                return
        else:
            user_id = message.from_user.id

        chat_id = message.chat.id

        async with self.locks['current_questions']:
            if chat_id in self.current_questions and user_id in self.current_questions[chat_id]:
                del self.current_questions[chat_id][user_id]

        async with self.locks['user_in_game']:
            if chat_id in self.user_in_game:
                self.user_in_game[chat_id].discard(user_id)

        async with self.locks['game_timers']:
            if chat_id in self.game_timers and user_id in self.game_timers[chat_id]:
                self.game_timers[chat_id][user_id].cancel()
                del self.game_timers[chat_id][user_id]

        await self.start_game(client, message)

    async def stats(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        db = Database('family100.db')
        score = db.get_user_score(message.chat.id, message.from_user.username)
        db.close()

        await message.reply_text(f"🏆Statistik Anda:\nNama Pengguna: {message.from_user.username}\nSkor: {score}")

    async def top(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        db = Database('family100.db')
        top_users = db.get_top_users()
        db.close()

        top_users_text = "Top 10 Pengguna:\n"
        for idx, (user_name, score) in enumerate(top_users, start=1):
            top_users_text += f"{idx}. {user_name}: {score} poin\n"

        await message.reply_text(top_users_text)

    async def topgrup(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        db = Database('family100.db')
        top_groups = db.get_top_groups()
        db.close()

        top_groups_text = "Top 10 Grup:\n"
        for idx, (chat_id, total_score) in enumerate(top_groups, start=1):
            top_groups_text += f"{idx}. Grup ID {chat_id}: {total_score} poin\n"

        await message.reply_text(top_groups_text)

    async def peraturan(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        rules_text = (
            "Peraturan Permainan Super Family 100:\n"
            "1. Ketik /mulai untuk memulai permainan.\n"
            "2. Setiap pertanyaan memiliki beberapa jawaban yang harus ditebak.\n"
            "3. Ketik jawaban Anda dan bot akan memeriksa kebenarannya.\n"
            "4. Ketik /nyerah untuk menyerah.\n"
            "5. Ketik /next untuk mendapatkan pertanyaan berikutnya.\n"
            "6. Poin akan diberikan berdasarkan jawaban yang benar."
        )
        await message.reply_text(rules_text)

    async def blacklist(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        if message.from_user.id != OWNER_ID:
            await message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return

        if len(message.command) < 2:
            await message.reply_text("ID pengguna atau ID grup tidak diberikan.")
            return

        try:
            target_id = int(message.command[1])
        except ValueError:
            await message.reply_text("ID pengguna atau ID grup tidak valid.")
            return

        if target_id < 0:
            async with self.locks['blacklisted_groups']:
                self.blacklisted_groups.add(target_id)
            await message.reply_text(f"Grup dengan ID {target_id} telah diblokir.")
        else:
            async with self.locks['blacklisted_users']:
                self.blacklisted_users.add(target_id)
            await message.reply_text(f"Pengguna dengan ID {target_id} telah diblokir.")

    async def whitelist(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        if message.from_user.id != OWNER_ID:
            await message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return

        if len(message.command) < 2:
            await message.reply_text("ID pengguna atau ID grup tidak diberikan.")
            return

        try:
            target_id = int(message.command[1])
        except ValueError:
            await message.reply_text("ID pengguna atau ID grup tidak valid.")
            return

        if target_id < 0:
            async with self.locks['blacklisted_groups']:
                self.blacklisted_groups.discard(target_id)
            await message.reply_text(f"Grup dengan ID {target_id} telah diizinkan kembali.")
        else:
            async with self.locks['blacklisted_users']:
                self.blacklisted_users.discard(target_id)
            await message.reply_text(f"Pengguna dengan ID {target_id} telah diizinkan kembali.")

    async def broadcast(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        if message.from_user.id != OWNER_ID:
            await message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return

        broadcast_message = message.text.split(maxsplit=1)[1] if len(message.text.split(maxsplit=1)) > 1 else ""
        if not broadcast_message:
            await message.reply_text("Pesan tidak diberikan.")
            return

        async with self.locks['registered_chats']:
            for chat_id in self.registered_chats:
                try:
                    await client.send_message(chat_id, broadcast_message)
                except Exception as e:
                    logging.error(f"Error broadcasting message to {chat_id}: {e}")

    def format_question(self, question, correct_answers, answerers):
        formatted_question = f"Pertanyaan: {question}\n"
        for i, (correct, users) in enumerate(zip(correct_answers, answerers), start=1):
            users_text = ", ".join(users) if users else "Belum ada"
            formatted_question += f"{i}. {correct} ({users_text})\n"
        return formatted_question

    def run(self):
        self.app.run()

if __name__ == "__main__":
    bot = SuperFamily100Bot()
    bot.run()
