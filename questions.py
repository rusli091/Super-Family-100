import random

# Daftar pertanyaan dan jawaban
QUESTIONS = [
    {
        "question": "Apa yang temanmu katakan saat mengumpat?",
        "answers": [("Sial", 10), ("Bodoh", 20), ("Gila", 30), ("Kampret", 40)]
    },
    {
        "question": "Sebutkan sesuatu yang Anda pakai di kaki.",
        "answers": [("Sepatu", 10), ("Sandal", 20), ("Kaos Kaki", 30), ("Boots", 40)]
    },
    {
        "question": "Sebutkan sesuatu yang bisa Anda temukan di pantai.",
        "answers": [("Pasir", 10), ("Kerang", 20), ("Ombak", 30), ("Pohon Kelapa", 40)]
    },
    {
        "question": "Sebutkan nama buah yang berwarna merah.",
        "answers": [("Apel", 10), ("Strawberi", 20), ("Ceri", 30), ("Delima", 40)]
    }
]

def get_random_question():
    # Pilih pertanyaan acak dari daftar
    question_set = random.choice(QUESTIONS)
    question = question_set["question"]
    answers = question_set["answers"]
    return question, answers

def check_answer(question, user_answer):
    for question_set in QUESTIONS:
        if question_set["question"] == question:
            for index, (answer, points) in enumerate(question_set["answers"]):
                if user_answer.lower() == answer.lower():
                    return index, points
    return -1, 0
