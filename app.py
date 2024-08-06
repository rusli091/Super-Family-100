import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
from dotenv import load_dotenv
from questions import get_random_question, check_answer
from database import Database

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
        # Implement rate limiting logic here
        return False

    async def start(self, client, message):
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

        if chat_id not in self.user_in_game:
            self.user_in_game[chat_id] = set()
        self.user_in_game[chat_id].add(user_id)

        question, answers = get_random_question()
        correct_answers = ["_" * len(ans) for ans, _ in answers]

        if chat_id not in self.current_questions:
            self.current_questions[chat_id] = {}

        self.current_questions[chat_id][user_id] = {
            "question": question,
            "answers": answers,
            "correct_answers": correct_answers
        }

        formatted_question = self.format_question(question, correct_answers)
        await message.reply_text(formatted_question)
        self.group_in_game.add(chat_id)

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

        if chat_id not in self.current_questions:
            return

        user_answer = message.text.strip()
        for uid in list(self.current_questions[chat_id].keys()):
            current_question = self.current_questions[chat_id][uid]
            question = current_question["question"]
            correct_answers = current_question["correct_answers"]
            all_answers = current_question["answers"]

            index, points = check_answer(question, user_answer)

            if index != -1:
                correct_answers[index] = all_answers[index][0]
                formatted_question = self.format_question(question, correct_answers)

                await message.reply_text(f"{message.from_user.first_name} menjawab benar! Poin: {points}\n{formatted_question}")

                user_name = message.from_user.username
                if user_name not in self.user_scores:
                    self.user_scores[user_name] = 0
                self.user_scores[user_name] += points

                if chat_id not in self.group_scores:
                    self.group_scores[chat_id] = {}
                if user_name not in self.group_scores[chat_id]:
                    self.group_scores[chat_id][user_name] = 0
                self.group_scores[chat_id][user_name] += points

                if all(ans != "_" * len(ans) for ans in correct_answers):
                    await message.reply_text("Pertanyaan telah selesai! Gunakan /next untuk pertanyaan berikutnya.")
                    del self.current_questions[chat_id][uid]

                    if chat_id in self.game_timers and uid in self.game_timers[chat_id]:
                        self.game_timers[chat_id][uid].cancel()
                        del self.game_timers[chat_id][uid]

                    self.user_in_game[chat_id].discard(uid)

    async def nyerah(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        if chat_id in self.current_questions and user_id in self.current_questions[chat_id]:
            del self.current_questions[chat_id][user_id]

            if chat_id in self.game_timers and user_id in self.game_timers[chat_id]:
                self.game_timers[chat_id][user_id].cancel()
                del self.game_timers[chat_id][user_id]

            self.user_in_game[chat_id].discard(user_id)
            await message.reply_text("Anda menyerah. Game Anda dihentikan.")
        else:
            await message.reply_text("Tidak ada permainan yang sedang berlangsung untuk Anda.")

    async def next(self, client, message):
        if await self.rate_limited(message.from_user.id):
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        if chat_id in self.current_questions:
            if user_id in self.current_questions[chat_id]:
                del self.current_questions[chat_id][user_id]

                if chat_id in self.game_timers and user_id in self.game_timers[chat_id]:
                    self.game_timers[chat_id][user_id].cancel()
                    del self.game_timers[chat_id][user_id]

                self.user_in_game[chat_id].discard(user_id)

        await self.start_game(client, message)

    async def stats(self, client, message):
        user_id = message.from_user.id
        user_name = message.from_user.username

        if user_name in self.user_scores:
            user_score = self.user_scores[user_name]
        else:
            user_score = 0

        sorted_users = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)
        global_rank = next((i + 1 for i, (username, _) in enumerate(sorted_users) if username == user_name), 'N/A')

        await message.reply_text(
            f"📊 Statistik Anda:\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Username: {user_name}\n"
            f"🏆 Score: {user_score}\n"
            f"🏅 Rank: {global_rank}\n"
        )

    async def top(self, client, message):
        sorted_users = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)
        top_users = "\n".join([f"{i + 1}. {username}: {score}" for i, (username, score) in enumerate(sorted_users[:10])])
        await message.reply_text(f"🏅 Top 10 Pemain:\n\n{top_users}")

    async def topgrup(self, client, message):
        sorted_groups = sorted(self.group_scores.items(), key=lambda x: sum(x[1].values()), reverse=True)
        top_groups = ""
        for i, (group_id, users_scores) in enumerate(sorted_groups[:10]):
            group_score = sum(users_scores.values())
            top_groups += f"{i + 1}. Group ID {group_id}: {group_score}\n"
            top_users = "\n".join([f"    {username}: {score}" for username, score in users_scores.items()])
            top_groups += top_users + "\n"
        
        await message.reply_text(f"🏅 Top 10 Grup:\n\n{top_groups}")

    async def peraturan(self, client, message):
        await message.reply_text(
            "📜 Peraturan Permainan Super Family 100:\n\n"
            "1. Setiap pertanyaan memiliki beberapa jawaban yang benar.\n"
            "2. Ketik jawaban Anda. Jika benar, poin akan diberikan.\n"
            "3. Anda bisa menyerah dengan mengetik /nyerah.\n"
            "4. Gunakan /next untuk pertanyaan berikutnya setelah pertanyaan selesai.\n"
            "5. Nikmati permainan dan jangan lupa bersenang-senang!"
        )

    async def blacklist(self, client, message):
        if str(message.from_user.id) != OWNER_ID:
            await message.reply_text("Hanya pemilik bot yang dapat mengakses perintah ini.")
            return

        if len(message.command) != 2:
            await message.reply_text("Gunakan format: /blacklist <user_id>")
            return

        user_id = int(message.command[1])
        self.blacklisted_users.add(user_id)
        await message.reply_text(f"Pengguna {user_id} telah di-blacklist.")

    async def whitelist(self, client, message):
        if str(message.from_user.id) != OWNER_ID:
            await message.reply_text("Hanya pemilik bot yang dapat mengakses perintah ini.")
            return

        if len(message.command) != 2:
            await message.reply_text("Gunakan format: /whitelist <user_id>")
            return

        user_id = int(message.command[1])
        self.blacklisted_users.discard(user_id)
        await message.reply_text(f"Pengguna {user_id} telah di-whitelist.")

    def format_question(self, question, correct_answers):
        formatted_answers = "\n".join([f"{i + 1}. {ans}" for i, ans in enumerate(correct_answers)])
        return f"{question}\n\n{formatted_answers}"

    def run(self):
        self.app.run()

if __name__ == "__main__":
    bot = SuperFamily100Bot()
    bot.run()
