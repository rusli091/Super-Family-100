import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
from dotenv import load_dotenv
from questions import get_random_question, check_answer
from database import Database
from rate_limiter import RateLimiter  # Import RateLimiter

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

        self.locks = {
            'user_scores': asyncio.Lock(),
            'group_scores': asyncio.Lock(),
            'current_questions': asyncio.Lock(),
            'game_timers': asyncio.Lock(),
            'user_in_game': asyncio.Lock()
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

        chat_id = message.chat.id
        user_id = message.from_user.id

        if chat_id in self.group_in_game and user_id in self.user_in_game.get(chat_id, set()):
            await message.reply_text("Permainan sudah dimulai untuk Anda di grup ini.")
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

        async with self.locks['current_questions']:
            if chat_id not in self.current_questions:
                self.current_questions[chat_id] = {}
            self.current_questions[chat_id][user_id] = {
                "question": question,
                "answers": answers,
                "correct_answers": correct_answers
            }

        formatted_question = self.format_question(question, correct_answers)
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

        async with self.locks['current_questions']:
            if chat_id not in self.current_questions:
                return

            user_answer = message.text.strip()
            for uid in list(self.current_questions[chat_id].keys()):
                current_question = self.current_questions[chat_id][uid]
                question = current_question["question"]
                correct_answers = current_question["correct_answers"]
                all_answers = current_question["answers"]

                if check_answer(user_answer, all_answers):
                    for i, (answer, points) in enumerate(all_answers):
                        if answer.lower() == user_answer.lower():
                            correct_answers[i] = answer
                            break

                    await message.reply_text(
                        f"✅ Jawaban benar: {user_answer} ({points} poin)"
                    )

                    async with self.locks['user_scores']:
                        if message.from_user.username not in self.user_scores:
                            self.user_scores[message.from_user.username] = 0
                        self.user_scores[message.from_user.username] += points

                    async with self.locks['group_scores']:
                        if chat_id not in self.group_scores:
                            self.group_scores[chat_id] = {}
                        if message.from_user.username not in self.group_scores[chat_id]:
                            self.group_scores[chat_id][message.from_user.username] = 0
                        self.group_scores[chat_id][message.from_user.username] += points

                    db = Database('family100.db')
                    db.update_score(chat_id, message.from_user.username, points)
                    db.close()

                    if all("_" not in ans for ans in correct_answers):
                        await message.reply_text("Semua jawaban sudah ditemukan. Gunakan /next untuk pertanyaan berikutnya.")
                        del self.current_questions[chat_id][uid]

                        async with self.locks['user_in_game']:
                            self.user_in_game[chat_id].discard(uid)

                        async with self.locks['game_timers']:
                            if uid in self.game_timers[chat_id]:
                                self.game_timers[chat_id][uid].cancel()
                                del self.game_timers[chat_id][uid]

    async def nyerah(self, client, message):
    if await self.rate_limited(message.from_user.id):
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    async with self.locks['current_questions']:
        if chat_id in self.current_questions and user_id in self.current_questions[chat_id]:
            del self.current_questions[chat_id][user_id]

            async with self.locks['game_timers']:
                if chat_id in self.game_timers and user_id in self.game_timers[chat_id]:
                    self.game_timers[chat_id][user_id].cancel()
                    del self.game_timers[chat_id][user_id]

            self.user_in_game[chat_id].discard(user_id)
            await message.reply_text("Anda menyerah. Game Anda dihentikan.")

async def next(self, client, message):
    if await self.rate_limited(message.from_user.id):
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    async with self.locks['current_questions']:
        if chat_id in self.current_questions and user_id in self.current_questions[chat_id]:
            del self.current_questions[chat_id][user_id]

            async with self.locks['game_timers']:
                if chat_id in self.game_timers and user_id in self.game_timers[chat_id]:
                    self.game_timers[chat_id][user_id].cancel()
                    del self.game_timers[chat_id][user_id]

            self.user_in_game[chat_id].discard(user_id)

    await self.start_game(client, message)

    async def stats(self, client, message):
        user_id = message.from_user.id
        user_name = message.from_user.username

        async with self.locks['user_scores']:
            user_score = self.user_scores.get(user_name, 0)
            global_rank = sorted(self.user_scores.items(), key=lambda item: item[1], reverse=True).index((user_name, user_score)) + 1

        await message.reply_text(
            f"📊 Statistik Anda:\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Username: {user_name}\n"
            f"🏆 Score: {user_score}\n"
            f"🏅 Rank: {global_rank}\n"
        )

    async def top(self, client, message):
        async with self.locks['user_scores']:
            top_users = sorted(self.user_scores.items(), key=lambda item: item[1], reverse=True)[:10]

        top_text = "Top 10 Pemain:\n" + "\n".join([f"{i+1}. {user}: {score}" for i, (user, score) in enumerate(top_users)])
        await message.reply_text(top_text)

    async def topgrup(self, client, message):
        chat_id = message.chat.id

        async with self.locks['group_scores']:
            if chat_id not in self.group_scores:
                await message.reply_text("Tidak ada skor untuk grup ini.")
                return

            top_users = sorted(self.group_scores[chat_id].items(), key=lambda item: item[1], reverse=True)[:10]

        top_text = f"Top 10 Pemain di Grup ini:\n" + "\n".join([f"{i+1}. {user}: {score}" for i, (user, score) in enumerate(top_users)])
        await message.reply_text(top_text)

    async def peraturan(self, client, message):
        rules_text = (
            "Aturan Bermain Super Family 100:\n"
            "1. Mulai permainan dengan /mulai\n"
            "2. Jawab pertanyaan yang diberikan\n"
            "3. Dapatkan poin untuk jawaban yang benar\n"
            "4. Gunakan /next untuk pertanyaan berikutnya\n"
            "5. Gunakan /nyerah jika ingin menyerah\n"
        )
        await message.reply_text(rules_text)

    async def blacklist(self, client, message):
        if str(message.from_user.id) != str(OWNER_ID):
            return

        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Penggunaan: /blacklist <user_id/group_id>")
            return

        target_id = int(args[1])
        if target_id < 0:
            self.blacklisted_groups.add(target_id)
            await message.reply_text(f"Grup {target_id} telah di-blacklist.")
        else:
            self.blacklisted_users.add(target_id)
            await message.reply_text(f"Pengguna {target_id} telah di-blacklist.")

    async def whitelist(self, client, message):
        if str(message.from_user.id) != str(OWNER_ID):
            return

        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Penggunaan: /whitelist <user_id/group_id>")
            return

        target_id = int(args[1])
        if target_id < 0:
            self.blacklisted_groups.discard(target_id)
            await message.reply_text(f"Grup {target_id} telah di-whitelist.")
        else:
            self.blacklisted_users.discard(target_id)
            await message.reply_text(f"Pengguna {target_id} telah di-whitelist.")

    def format_question(self, question, correct_answers):
        formatted_question = question + "\n\n" + "\n".join(correct_answers)
        return formatted_question

    def run(self):
        self.app.run()

if __name__ == "__main__":
    bot = SuperFamily100Bot()
    bot.run()
