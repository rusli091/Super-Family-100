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
        self.app.add_handler(MessageHandler(self.play, filters.command("play")))
        self.app.add_handler(MessageHandler(self.nyerah, filters.command("nyerah")))
        self.app.add_handler(MessageHandler(self.next, filters.command("next")))
        self.app.add_handler(MessageHandler(self.stats, filters.command("stats")))
        self.app.add_handler(MessageHandler(self.top, filters.command("top")))
        self.app.add_handler(MessageHandler(self.topgrup, filters.command("topgrup")))
        self.app.add_handler(MessageHandler(self.peraturan, filters.command("peraturan")))
        self.app.add_handler(MessageHandler(self.blacklist, filters.command("blacklist")))
        self.app.add_handler(MessageHandler(self.whitelist, filters.command("whitelist")))
        self.app.add_handler(MessageHandler(self.handle_answer, filters.text & filters.group))

    async def start(self, client, message):
        user_fullname = message.from_user.first_name
        user_id = message.from_user.id

        # Check if the message is a reply to a bot message
        if message.reply_to_message and message.reply_to_message.from_user.is_bot:
            # Bot message detected, proceed to start the game
            await self.start_game(client, message)
        else:
            # Normal command /start, send welcome message and instructions
            welcome_text = (
                f"Halo {user_fullname}, ayo kita main Super Family 100.\n"
                "/play : mulai game\n"
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
            "/play : mulai game\n"
            "/nyerah : menyerah dari game\n"
            "/next : Pertanyaan berikutnya\n"
            "/help : membuka pesan bantuan\n"
            "/stats : melihat statistik kamu\n"
            "/top : lihat top skor global\n"
            "/topgrup : lihat top skor grup\n"
            "/peraturan : aturan bermain\n"
        )

    async def play(self, client, message):
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

        # Set game timer for 1 minute for the user
        if chat_id not in self.game_timers:
            self.game_timers[chat_id] = {}
        self.game_timers[chat_id][user_id] = asyncio.get_running_loop().call_later(60, self.next_game_question, client, chat_id, user_id)

        # Example database operation
        db = Database('family100.db')
        db.update_score(chat_id, message.from_user.username, 0)
        db.close()

    async def next_game_question(self, client, chat_id, user_id):
        await client.send_message(chat_id, f"/next {user_id}")

    async def handle_answer(self, client, message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if chat_id not in self.current_questions or user_id not in self.current_questions[chat_id]:
            return

        user_answer = message.text.strip()
        current_question = self.current_questions[chat_id][user_id]
        question = current_question["question"]
        correct_answers = current_question["correct_answers"]
        all_answers = current_question["answers"]

        index, points = check_answer(question, user_answer)

        if index != -1:
            correct_answers[index] = all_answers[index][0]
            formatted_question = self.format_question(question, correct_answers)
            
            await message.reply_text(f"Jawaban benar! Poin: {points}\n{formatted_question}")

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
                del self.current_questions[chat_id][user_id]

                # Cancel game timer for this user
                if chat_id in self.game_timers and user_id in self.game_timers[chat_id]:
                    self.game_timers[chat_id][user_id].cancel()
                    del self.game_timers[chat_id][user_id]

                self.user_in_game[chat_id].discard(user_id)
        else:
            await message.reply_text(f"Jawaban salah! Coba lagi.\n{self.format_question(question, correct_answers)}")

    async def nyerah(self, client, message):
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
            else:
                await message.reply_text("Tidak ada permainan yang sedang berlangsung untuk Anda.")
        else:
            await message.reply_text("Tidak ada permainan yang sedang berlangsung.")

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
        sorted_users = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        top_scores = [f"{i+1}. {username}: {score}" for i, (username, score) in enumerate(sorted_users)]
        await message.reply_text("🏆 Top 10 Skor Global:\n" + "\n".join(top_scores))

    async def topgrup(self, client, message):
        chat_id = message.chat.id

        if chat_id not in self.group_scores:
            await message.reply_text("Belum ada skor di grup ini.")
            return

        sorted_users = sorted(self.group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)[:10]
        top_scores = [f"{i+1}. {username}: {score}" for i, (username, score) in enumerate(sorted_users)]
        await message.reply_text("🏆 Top 10 Skor Grup:\n" + "\n".join(top_scores))

    async def peraturan(self, client, message):
        await message.reply_text(
            "📜 Peraturan Main Super Family 100 📜\n\n"
            "1. Ketik /play untuk mulai permainan.\n"
            "2. Jawab pertanyaan dengan mengetikkan jawaban Anda.\n"
            "3. Anda memiliki waktu 60 detik untuk menjawab setiap pertanyaan.\n"
            "4. Gunakan /nyerah jika ingin menyerah dari permainan.\n"
            "5. Gunakan /next untuk pertanyaan berikutnya setelah pertanyaan saat ini selesai.\n"
            "6. Jangan curang, bersikap sportif.\n"
            "7. Selamat bersenang-senang!"
        )

    async def blacklist(self, client, message):
        if message.from_user.id not in ADMINS:
            await message.reply_text("Hanya admin yang bisa menggunakan perintah ini.")
            return

        target_id = int(message.command[1])
        self.blacklisted_users.add(target_id)
        await message.reply_text(f"Pengguna {target_id} telah di-blacklist.")

    async def whitelist(self, client, message):
        if message.from_user.id not in ADMINS:
            await message.reply_text("Hanya admin yang bisa menggunakan perintah ini.")
            return

        target_id = int(message.command[1])
        self.blacklisted_users.discard(target_id)
        await message.reply_text(f"Pengguna {target_id} telah di-whitelist.")

    def format_question(self, question, correct_answers):
        answer_lines = [f"{i+1}. {answer}" for i, answer in enumerate(correct_answers)]
        formatted_question = f"{question}\n\n" + "\n".join(answer_lines)
        return formatted_question

    def run(self):
        print("Bot is running...")
        self.app.run()

if __name__ == "__main__":
    bot = SuperFamily100Bot()
    bot.run()
