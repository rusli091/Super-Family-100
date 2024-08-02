import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
from dotenv import load_dotenv
from questions import get_random_question, check_answer
from database import get_db_connection, init_db

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
        self.app.add_handler(MessageHandler(self.handle_answer, filters.text & filters.private))

    async def start(self, client, message):
        user_fullname = message.from_user.first_name
        user_id = message.from_user.id

        # Check if the message is a reply to a bot message
        if message.reply_to_message and message.reply_to_message.from_user.is_bot:
            # Bot message detected, proceed to start the game
            await self.start_game(client, message)
        else:
            # Normal command /start, send welcome message and instructions
            await message.reply_text(
                f"Halo {user_fullname}, ayo kita main Super Family 100.\n"
                "/play : mulai game\n"
                "/nyerah : menyerah dari game\n"
                "/next : Pertanyaan berikutnya\n"
                "/help : membuka pesan bantuan\n"
                "/stats : melihat statistik kamu\n"
                "/top : lihat top skor global\n"
                "/topgrup : lihat top skor grup\n"
                "/peraturan : aturan bermain\n\n"
                "Klik /start setelah memasukkan bot ini ke grup untuk memulai permainan."
            )

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
        if chat_id in self.group_in_game:
            await message.reply_text("Permainan sudah dimulai di grup ini.")
            return

        await self.start_game(client, message)

    async def start_game(self, client, message):
        question, answers = get_random_question()
        correct_answers = ["_" * len(ans) for ans, _ in answers]

        client.current_question = question
        client.correct_answers = correct_answers
        client.all_answers = answers

        formatted_question = self.format_question(question, correct_answers)
        await message.reply_text(formatted_question)
        self.group_in_game.add(message.chat.id)

        # Set game timer for 1 minute
        self.game_timers[message.chat.id] = asyncio.get_running_loop().call_later(60, self.next_game_question, client, message.chat.id)

        # Example database operation
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO groups (id) VALUES (?)", (message.chat.id,))
            conn.commit()

    async def next_game_question(self, client, chat_id):
        await client.send_message(chat_id, "/next")

    async def handle_answer(self, client, message):
        if not hasattr(client, 'current_question'):
            return

        user_answer = message.text.strip()
        question = client.current_question
        correct_answers = client.correct_answers
        all_answers = client.all_answers

        index, points = check_answer(question, user_answer)

        if index != -1:
            correct_answers[index] = all_answers[index][0]
            formatted_question = self.format_question(question, correct_answers)
            
            await message.reply_text(f"Jawaban benar! Poin: {points}\n{formatted_question}")

            user_name = message.from_user.username
            if user_name not in self.user_scores:
                self.user_scores[user_name] = 0
            self.user_scores[user_name] += points

            chat_id = message.chat.id
            if chat_id not in self.group_scores:
                self.group_scores[chat_id] = {}
            if user_name not in self.group_scores[chat_id]:
                self.group_scores[chat_id][user_name] = 0
            self.group_scores[chat_id][user_name] += points

            if all(ans != "_" * len(ans) for ans in correct_answers):
                await message.reply_text("Pertanyaan telah selesai! Gunakan /next untuk pertanyaan berikutnya.")
                del client.current_question
                del client.correct_answers
                del client.all_answers

                # Cancel game timer for this group
                if chat_id in self.game_timers:
                    self.game_timers[chat_id].cancel()
                    del self.game_timers[chat_id]

    async def nyerah(self, client, message):
        if hasattr(client, 'current_question'):
            del client.current_question
            del client.correct_answers
            del client.all_answers

            chat_id = message.chat.id
            if chat_id in self.game_timers:
                self.game_timers[chat_id].cancel()
                del self.game_timers[chat_id]

            await message.reply_text("Anda menyerah. Game dihentikan.")

    async def next(self, client, message):
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
        top_list = "\n".join(f"{self.get_rank_emoji(rank)} {username} - {user_id} - ({score})🏆" for rank, ((username, user_id), score) in enumerate(sorted_users[:10], start=1))
        await message.reply_text(f"🏆 Top Player Global:\n{top_list}")

    async def topgrup(self, client, message):
        sorted_groups = sorted(self.group_scores.items(), key=lambda x: sum(x[1].values()), reverse=True)
        top_list = "\n".join(f"{self.get_rank_emoji(rank)} {self.get_group_name(chat_id)} - {self.get_group_link(chat_id)} - ({sum(scores.values())})🏆" for rank, (chat_id, scores) in enumerate(sorted_groups[:10], start=1))
        await message.reply_text(f"🏆 Top Group Global:\n{top_list}")

    async def peraturan(self, client, message):
        rules = """
        1. Jaga kekompakan dan persatuan keluarga.
        2. Dilarang membuat masalah.
        3. Dilarang menyinggung perasaan.
        4. Jika ada yg menyinggung perasaan maka harus meminta maaf
        5. Selalu menghargai anggota yg lain.
        """
        await message.reply_text(rules)

    async def blacklist(self, client, message):
        if message.from_user.id == OWNER_ID:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                self.blacklisted_users.add(user_id)
                await message.reply_text("User telah berhasil dimasukkan dalam daftar hitam.")
            else:
                await message.reply_text("Balas pesan pengguna untuk memasukkan dalam daftar hitam.")
        else:
            await message.reply_text("Anda tidak memiliki izin untuk menjalankan perintah ini.")

    async def whitelist(self, client, message):
        if message.from_user.id == OWNER_ID:
            if message.reply_to_message:
                user_id = message.reply_to_message.from_user.id
                if user_id in self.blacklisted_users:
                    self.blacklisted_users.remove(user_id)
                    await message.reply_text("User telah berhasil dihapus dari daftar hitam.")
                else:
                    await message.reply_text("User tidak ada dalam daftar hitam.")
            else:
                await message.reply_text("Balas pesan pengguna untuk menghapus dari daftar hitam.")
        else:
            await message.reply_text("Anda tidak memiliki izin untuk menjalankan perintah ini.")

    def format_question(self, question, correct_answers):
        formatted_question = f"{question}\n\nJawaban: {' atau '.join(correct_answers)}"
        return formatted_question

    def get_rank_emoji(self, rank):
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return f"{rank}. "

    def get_group_name(self, chat_id):
        # Placeholder function, replace with actual logic to get group name based on chat_id
        return f"Group-{chat_id}"

    def get_group_link(self, chat_id):
        # Placeholder function, replace with actual logic to get group link based on chat_id
        return f"@group{chat_id}"

    def run(self):
        self.app.run()

if __name__ == "__main__":
    bot = SuperFamily100Bot()
    bot.run()
