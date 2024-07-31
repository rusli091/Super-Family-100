# utils.py
import asyncio

async def send_timed_message(client, chat_id, text, duration):
    message = await client.send_message(chat_id, text)
    await asyncio.sleep(duration)
    await message.delete()

def format_leaderboard(leaderboard):
    formatted = "Papan Peringkat:\n"
    for i, (player, score) in enumerate(leaderboard, start=1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
        formatted += f"{i}. {medal} {player}: {score}\n"
    return formatted