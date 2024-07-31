import random

questions = [
    ("Sebutkan nama buah yang berwarna merah!", [
        ("apel", 30),
        ("semangka", 25),
        ("strawberry", 20),
        ("cherry", 15),
        ("delima", 10)
    ]),
    ("Sebutkan alat transportasi umum!", [
        ("bus", 30),
        ("kereta", 25),
        ("taksi", 20),
        ("angkot", 15),
        ("ojek", 10)
    ]),
    # Tambahkan lebih banyak pertanyaan di sini
]

def get_random_question():
    return random.choice(questions)

def check_answer(question, user_answer):
    for q, answers in questions:
        if q == question:
            for index, (answer, points) in enumerate(answers):
                if user_answer.lower() == answer.lower():
                    return index, points
    return -1, 0

# Contoh Penggunaan:
question, answers = get_random_question()
print(f"Pertanyaan: {question}")

user_answer = "Apel"  # Contoh jawaban pengguna
index, points = check_answer(question, user_answer)

if index != -1:
    print(f"Jawaban benar! Jawaban ke-{index + 1} dengan {points} poin.")
else:
    print("Jawaban salah.")
