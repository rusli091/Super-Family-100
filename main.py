import logging
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler
from dotenv import load_dotenv
from questions import get_random_question, check_answer
import pickle

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

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
        self.user_scores = self.load_data('user_scores.pkl', {})
        self.group_scores = self.load_data('group_scores.pkl', {})
        self.blacklisted_users = self.load_data('blacklisted_users.pkl', set())
        self.blacklisted_groups = self.load_data('blacklisted_groups.pkl', set())

    def save_data(self, filename, data):
        with open(filename, 'wb') as f:
            pickle.dump(data, f)

    def load_data(self, filename, default):
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return default

    async def start(self, client, message):
        user_fullname = message.from_user.first_name
        chat_id = message.chat.id
        if message.chat.type in ["group", "supergroup"]:
            logger.info(f"Bot joined a group: {message.chat.title} ({chat_id})")
        else:
            logger.info(f"User started bot: {user_fullname} ({message.from_user.id})")

        keyboard = [
            [InlineKeyboardButton("Support", url="https://t.me/+bRlP2S66_g45MTFl")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            f"Halo {user_fullname}, ayo kita main Super Family 100.\n"
            "/play : mulai game\n"
            "/nyerah : menyerah dari game\n"
            "/next : Pertanyaan berikutnya\n"
            "/help : membuka pesan bantuan\n"
            "/stats : melihat statistik kamu\n"
            "/top : lihat top skor global\n"
            "/topgrup : lihat top skor grup\n"
            "/peraturan : aturan bermain\n",
            reply_markup=reply_markup
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

    def format_question(self, question, correct_answers):
        answer_lines = [f"{i+1}. {answer}" for i, answer in enumerate(correct_answers)]
        return f"{question}\n" + "\n".join(answer_lines)

    def update_question_format(self, question, correct_answers):
        return self.format_question(question, correct_answers)

    async def play(self, client, message):
        try:
            if message.from_user.id in self.blacklisted_users or message.chat.id in self.blacklisted_groups:
                await message.reply_text("Anda atau grup ini telah diblokir dari permainan.")
                return

            question, answers = get_random_question()
            client.current_question = question
            client.correct_answers = ["_" * len(ans) for ans, _ in answers]
            client.all_answers = answers
            formatted_question = self.format_question(question, client.correct_answers)
            await message.reply_text(formatted_question)
        except Exception as e:
            logger.error(f"Terjadi kesalahan saat memulai permainan: {str(e)}")
            await message.reply_text("Maaf, terjadi kesalahan. Pastikan bot memiliki izin yang cukup dalam grup ini.")

    async def handle_answer(self, client, message):
        if not hasattr(client, 'current_question'):
            return

        user_answer = message.text.strip()
        question = client.current_question
        correct_answers = client.correct_answers
        all_answers = client.all_answers

        logger.debug(f"User answer: {user_answer}")
        logger.debug(f"Current question: {question}")
        logger.debug(f"Correct answers so far: {correct_answers}")

        index, points = check_answer(question, user_answer)
        logger.debug(f"Index of the correct answer: {index}, Points: {points}")
        
        if index != -1:
            correct_answers[index] = all_answers[index][0]
            formatted_question = self.update_question_format(question, correct_answers)
            
            await message.reply_text(f"Jawaban benar! Poin: {points}\n{formatted_question}")

            user_name = message.from_user.username or message.from_user.first_name
            if user_name not in self.user_scores:
                self.user_scores[user_name] = 0
            self.user_scores[user_name] += points

            chat_id = message.chat.id
            if chat_id not in self.group_scores:
                self.group_scores[chat_id] = {}
            if user_name not in self.group_scores[chat_id]:
                self.group_scores[chat_id][user_name] = 0
            self.group_scores[chat_id][user_name] += points

            self.save_data('user_scores.pkl', self.user_scores)
            self.save_data('group_scores.pkl', self.group_scores)

            del client.current_question
            del client.correct_answers
            del client.all_answers

    async def nyerah(self, client, message):
        await message.reply_text("Anda telah menyerah dari game.")

    async def next(self, client, message):
        question, answers = get_random_question()
        client.current_question = question
        client.correct_answers = ["_" * len(ans) for ans, _ in answers]
        client.all_answers = answers
        formatted_question = self.format_question(question, client.correct_answers)
        await message.reply_text(formatted_question)

    async def stats(self, client, message):
        user_name = message.from_user.username or message.from_user.first_name
        user_id = message.from_user.id
        user_score = self.user_scores.get(user_name, 0)
        
        global_rank = sum(1 for score in self.user_scores.values() if score > user_score) + 1

        stats_message = (
            f"Your Game Stats\n"
            f"🆔 ID: {user_id}\n"
            f"🏅 Name: {user_name}\n"
            f"🌐 Score: {user_score}\n"
            f"🏆 Global Rank: {global_rank}\n"
        )
        await message.reply_text(stats_message)

    async def top(self, client, message):
        top_players = sorted(self.user_scores.items(), key=lambda x: x[1], reverse=True)
        formatted_top_players = [
            f"{i + 1}. {'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else '🏅'} {player} - {score}"
            for i, (player, score) in enumerate(top_players[:10])
        ]
        await message.reply_text("Top Player Global:\n" + "\n".join(formatted_top_players))

    async def topgrup(self, client, message):
        chat_id = message.chat.id
        if chat_id not in self.group_scores:
            self.group_scores[chat_id] = {}
        
        top_group_players = sorted(self.group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)
        formatted_top_group_players = [
            f"{i + 1}. {'🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else '🏅'} {player} - {score}"
            for i, (player, score) in enumerate(top_group_players[:10])
        ]
        await message.reply_text("Top Player Grup:\n" + "\n".join(formatted_top_group_players))

    async def peraturan(self, client, message):
        await message.reply_text(
            "<b>Peraturan bermain adalah:</b>\n\n"
            "1. Mulai permainan dengan mengetik /play.\n"
            "2. Anda akan diberikan pertanyaan dan harus menjawabnya.\n"
            "3. Gunakan /nyerah untuk menyerah dari permainan.\n"
            "4. Gunakan /next untuk mendapatkan pertanyaan berikutnya.\n"
            "5. Gunakan /stats untuk melihat statistik Anda.\n"
            "6. Gunakan /top untuk melihat top skor global.\n"
            "7. Gunakan /topgrup untuk melihat top skor grup.\n"
            "8. Gunakan /help untuk melihat daftar perintah.\n\n",
            parse_mode='HTML'
        )

    async def blacklist(self, client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Penggunaan: /blacklist [user_id/grup_id]")
            return

        try:
            target_id = int(args[1])
            if target_id < 0:
                self.blacklisted_groups.add(target_id)
                await message.reply_text(f"Grup {target_id} telah diblacklist.")
                logger.info(f"Group {target_id} blacklisted by {message.from_user.username or message.from_user.first_name}.")
            else:
                self.blacklisted_users.add(target_id)
                await message.reply_text(f"User {target_id} telah diblacklist.")
                logger.info(f"User {target_id} blacklisted by {message.from_user.username or message.from_user.first_name}.")
            
            self.save_data('blacklisted_users.pkl', self.blacklisted_users)
            self.save_data('blacklisted_groups.pkl', self.blacklisted_groups)
        except ValueError:
            await message.reply_text("ID harus berupa angka.")

    async def whitelist(self, client, message):
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Penggunaan: /whitelist [user_id/grup_id]")
            return

        try:
            target_id = int(args[1])
            if target_id < 0:
                self.blacklisted_groups.discard(target_id)
                await message.reply_text(f"Grup {target_id} telah dihapus dari blacklist.")
                logger.info(f"Group {target_id} removed from blacklist by {message.from_user.username or message.from_user.first_name}.")
            else:
                self.blacklisted_users.discard(target_id)
                await message.reply_text(f"User {target_id} telah dihapus dari blacklist.")
                logger.info(f"User {target_id} removed from blacklist by {message.from_user.username or message.from_user.first_name}.")
            
            self.save_data('blacklisted_users.pkl', self.blacklisted_users)
            self.save_data('blacklisted_groups.pkl', self.blacklisted_groups)
        except ValueError:
            await message.reply_text("ID harus berupa angka.")

    def run(self):
        self.app.add_handler(MessageHandler(self.start, filters.command("start")))
        self.app.add_handler(MessageHandler(self.bantuan, filters.command("help")))
        self.app.add_handler(MessageHandler(self.play, filters.command("play")))
        self.app.add_handler(MessageHandler(self.handle_answer, filters.text & ~filters.command))
        self.app.add_handler(MessageHandler(self.nyerah, filters.command("nyerah")))
        self.app.add_handler(MessageHandler(self.next, filters.command("next")))
        self.app.add_handler(MessageHandler(self.stats, filters.command("stats")))
        self.app.add_handler(MessageHandler(self.top, filters.command("top")))
        self.app.add_handler(MessageHandler(self.topgrup, filters.command("topgrup")))
        self.app.add_handler(MessageHandler(self.peraturan, filters.command("peraturan")))
        self.app.add_handler(MessageHandler(self.blacklist, filters.command("blacklist") & filters.user(OWNER_ID)))
        self.app.add_handler(MessageHandler(self.whitelist, filters.command("whitelist") & filters.user(OWNER_ID)))
        self.app.run()

if __name__ == "__main__":
    try:
        bot = SuperFamily100Bot()
        bot.run()
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {str(e)}")