import random

# Daftar pertanyaan dan jawaban
questions = [
    {
        "question": "Apa yang temanmu katakan saat mengumpat?",
        "answers": [("Sial", 1), ("Bodoh", 1), ("Gila", 1), ("Kampret", 1)]
    },
    {
        "question": "Sebutkan sesuatu yang Anda pakai di kaki.",
        "answers": [("Sepatu", 1), ("Sandal", 1), ("Kaos Kaki", 1), ("Boots", 1)]
    },
    {
        "question": "Sebutkan sesuatu yang bisa Anda temukan di pantai.",
        "answers": [("Pasir", 1), ("Kerang", 1), ("Ombak", 1), ("Pohon Kelapa", 1)]
    },
    {
        "question": "Sebutkan nama buah yang berwarna merah.",
        "answers": [("Apel", 1), ("Strawberi", 1), ("Ceri", 1), ("Delima", 1)]
    },
    {
        "question": "Animals On The Sea?",
        "answers": [("Crab", 1), ("Fish", 1), ("Shark", 1), ("Sealion", 1), ("Dolphin", 1), ("Turtle", 1)]
    },
    {
        "question": "Apa Saja Keuntungan Menjadi Orang Gila?",
        "answers": [("Terkenal", 1), ("Makan Gratis", 1), ("Selalu Riang", 1), ("Ditakuti Preman", 1), ("Pusat Perhatian", 1)]
    },
    {
        "question": "Aduh Aku Digigit…",
        "answers": [("Nyamuk", 1), ("Anjing", 1), ("Ular", 1), ("Tikus", 1), ("Pacarku", 1)]
    },
    {
        "question": "Apa Saja Yang Ada Didalam Pesawat?",
        "answers": [("Pramugara", 1), ("Pramugari", 1), ("Kokpit", 1), ("Kamar Kecil", 1), ("Pelampung", 1), ("Penumpang", 1), ("Pilot", 1)]
    },
    {
        "question": "Apa Yang Biasanya Sering Lupa Dibawa?",
        "answers": [("Uang", 1), ("Dompet", 1), ("Handphone", 1), ("Kunci", 1), ("Kacamata", 1), ("STNK", 1)]
    },
    {
        "question": "Apa Yang Dilakukan Orang Di Stadion Sambil Menunggu Pertandingan Dimulai?",
        "answers": [("Ngobrol", 1), ("Makan", 1), ("Minum", 1), ("Pemanasan", 1), ("Tidur", 1), ("Baca Koran", 1)]
    },
    {
        "question": "Apa Yang Dilakukan Orang Bila Mengantuk?",
        "answers": [("Tidur", 1), ("Menguap", 1), ("Minum Kopi", 1), ("Cuci Muka", 1)]
    },
    {
        "question": "Apa Yang Mudah Larut Dalam Air?",
        "answers": [("Teh", 1), ("Kopi", 1), ("Gula", 1), ("Garam", 1), ("Sirup", 1)]
    },
    {
        "question": "Apa Yang Terjadi Jika Sakit Hati?",
        "answers": [("Nangis", 1), ("Curhat", 1), ("Stress", 1), ("Jadi Gila", 1), ("Sedih", 1)]
    },
    {
        "question": "Apa Yang Diperlukan Orang Saat Didaerah Berkabut?",
        "answers": [("Lampu", 1), ("Senter", 1), ("Jaket", 1), ("Kompor", 1), ("Korek Api", 1)]
    },
    {
        "question": "Bahan Bakar Yang Berasal Dari Alam?",
        "answers": [("Bensin", 1), ("Solar", 1), ("Batu Bara", 1), ("Minyak Tanah", 1), ("Gas LPG", 1)]
    },
    {
        "question": "Barang Bekas Apa Yang Biasanya Dijual Oleh Tukang Loak Di Pinggir Jalan?",
        "answers": [("Sepatu", 1), ("Sandal", 1), ("Kardus", 1), ("Jaket", 1), ("Tape", 1), ("Onderdil", 1)]
    },
    {
        "question": "Berapa Lama Orang Menjemur Kasur?",
        "answers": [("Satu Jam", 1), ("Empat Jam", 1), ("Seharian", 1)]
    },
    {
        "question": "Batuan Mineral Yang Berharga Tinggi?",
        "answers": [("Berlian", 1), ("Intan", 1), ("Mutiara", 1), ("Permata", 1), ("Delima", 1)]
    },
    {
        "question": "Benda Yang Sering Ada Dilaboraturim?",
        "answers": [("Jas", 1), ("Alat Peraga", 1), ("Mikroskop", 1), ("Tabung", 1)]
    },
    {
        "question": "Berbagai Macam Rasa Susu?",
        "answers": [("Manis", 1), ("Coklat", 1), ("Kopi", 1), ("Strawberry", 1), ("Mocca", 1), ("Grape", 1), ("Nanas", 1), ("Pisang", 1)]
    },
    {
        "question": "Bila Lihat Wanita Berambut Indah Pengennya?",
        "answers": [("Membelai", 1), ("Melirik", 1), ("Kagum", 1), ("Bersiul", 1), ("Memuji", 1)]
    },
    {
        "question": "Bunga Dengan Warna Merah?",
        "answers": [("Mawar", 1), ("Kembang Sepatu", 1), ("Soka", 1), ("Jengger Ayam", 1), ("Anturuim", 1)]
    },
    {
        "question": "Buah Yang Berawalan Huruf P?",
        "answers": [("Pisang", 1), ("Pear", 1), ("Pepaya", 1)]
    },
    {
        "question": "Cara Efektif Membunuh Nyamuk?",
        "answers": [("Semprot", 1), ("Lempar", 1), ("Cablek", 1), ("Injek", 1), ("Tabok", 1), ("Pites", 1), ("Gigit", 1)]
    },
    {
        "question": "Cara Pengawetan Sayur dan Buah?",
        "answers": [("Pengeringan", 1), ("Pengalengan", 1), ("Pengasinan", 1), ("Pemasinan", 1), ("Pelumatan", 1)]
    },
    {
        "question": "Ciri Ciri Gajah?",
        "answers": [("Besar", 1), ("Belalai", 1), ("Gading", 1), ("Telinga Lebar", 1), ("Kulit Tebal", 1)]
    },
    {
        "question": "Ciri Ciri Negara Mesir?",
        "answers": [("Piramida", 1), ("Sungai Nil", 1), ("Firaun", 1), ("Mumi", 1), ("Sphinx", 1)]
    },
    {
        "question": "Ciri Orang Emosi?",
        "answers": [("Main Pukul", 1), ("Pergi Lokalisasi", 1), ("Bunuh Orang", 1)]
    },
    {
        "question": "Disaat Apa Orang Mematikan Ponsel?",
        "answers": [("Ujian", 1), ("Kuliah", 1), ("Pacaran", 1), ("Ibadah", 1), ("Tidur", 1), ("Rapat", 1)]
    },
    {
        "question": "Fasilitas Berternak Ikan?",
        "answers": [("Jala", 1), ("Tambak", 1), ("Saringan", 1)]
    },
    {
        "question": "Fasilitas Email Gratis?",
        "answers": [("Gmail", 1), ("Ymail", 1), ("Msn", 1), ("Hotmail", 1)]
    },
    {
        "question": "Fungsi Handphone?",
        "answers": [("Sms", 1), ("Telepon", 1), ("Foto", 1), ("Internet", 1), ("Main Game", 1)]
    },
    {
        "question": "Hasil Hasil Perkebunan?",
        "answers": [("Kopi", 1), ("Coklat", 1), ("Karet", 1), ("Lada", 1), ("Cengkeh", 1)]
    },
        {
        "question": "Hewan Mamalia?",
        "answers": [("Anjing", 1), ("Kucing", 1), ("Singa", 1), ("Kelinci", 1), ("Beruang", 1)]
    },
    {
        "question": "Hewan Berbulu Tebal?",
        "answers": [("Beruang", 1), ("Panda", 1), ("Kera", 1), ("Domba", 1), ("Kucing", 1)]
    },
    {
        "question": "Hiburan Apa Yang Ada Dipesta Ulang Tahun?",
        "answers": [("Band", 1), ("Badut", 1), ("Sulap", 1), ("Kuis", 1), ("Game", 1)]
    },
    {
        "question": "Imunisasi Dari Pihak Posyandu / Klinik?",
        "answers": [("Polio", 1), ("Campak", 1), ("Cacar", 1), ("BCG", 1), ("DPT", 1), ("Demam Tifoid", 1)]
    },
    {
        "question": "Jenis Anjing Terkenal?",
        "answers": [("Dalmation", 1), ("Buldog", 1), ("Pom", 1)]
    },
    {
        "question": "Jenis Hewan Vertebrata?",
        "answers": [("Reptilia", 1), ("Aves", 1), ("Amphibia", 1), ("Mamalia", 1), ("Pisces", 1)]
    },
    {
        "question": "Jenis Penyakit Kulit?",
        "answers": [("Panu", 1), ("Kurap", 1), ("Gatal-gatal", 1), ("Koreng", 1), ("Kadas", 1), ("Kutu air", 1)]
    },
    {
        "question": "Jenis Jenis Energi?",
        "answers": [("Listrik", 1), ("Panas Bumi", 1), ("Gas Alam", 1), ("Tenaga Air", 1)]
    },
    {
        "question": "Jenis Jenis Wiraswasta?",
        "answers": [("Nelayan", 1), ("Bertani", 1), ("Provider", 1), ("Makelar", 1), ("Travelling", 1)]
    },
    {
        "question": "Jenis Kursi?",
        "answers": [("Sofa", 1), ("Kursi Santai", 1), ("Kursi Goyang", 1), ("Kursi Roda", 1), ("Kursi Plastik", 1)]
    },
    {
        "question": "Jenis Makanan Atau Minuman Yang Disukai Untuk Berbuka Puasa?",
        "answers": [("Air Putih", 1), ("Teh Hangat", 1), ("Es Kelapa Muda", 1), ("Gorengan", 1), ("Kolak", 1)]
    },
    {
        "question": "Jenis Sampah?",
        "answers": [("Organik", 1), ("Anorganik", 1), ("B3", 1)]
    },
    {
        "question": "Julukan Suporter Indonesia?",
        "answers": [("Bonek", 1), ("The Jack", 1), ("Bobotoh", 1)]
    },
    {
        "question": "Kalau Cewe Liat Tikus?",
        "answers": [("Lari", 1), ("Teriak", 1), ("Pingsan", 1), ("Loncat", 1), ("Kaget", 1)]
    },
    {
        "question": "Kalau Kamu Dirumah Sendirian Kamu Bakal?",
        "answers": [("Tidur", 1), ("Belajar", 1), ("Telpon", 1), ("Dengerin Musik", 1)]
    }
    {
        "question": "Kebiasaan Waktu Tidur",
        "answers": [("Mendengkur", 1), ("Menguap", 1), ("Ngiler", 1)]
    },
    {
        "question": "Label Musik Indonesia",
        "answers": [("Sony", 1), ("Aquarius", 1), ("Buletin", 1), ("Billboard", 1), ("Emi", 1)]
    },
    {
        "question": "Lagu Safe Band?",
        "answers": [("Lupakan Aku", 1), ("Lupakan Kehangatan", 1), ("Seumur dunia", 1)]
    },
    {
        "question": "Macam Macam Hantu",
        "answers": [("Pocong", 1), ("Kuntilanak", 1), ("Sundel Bolong", 1), ("Kolor Ijo", 1), ("Endas Glundung", 1), ("Grandong", 1)]
    },
    {
        "question": "Macam Macam Tepung",
        "answers": [("Kanji", 1), ("Beras", 1), ("Terigu", 1)]
    },
    {
        "question": "Macam Macam Pisang",
        "answers": [("Raja", 1), ("Ambon", 1), ("Sepatu", 1), ("Tanduk", 1), ("Mas", 1), ("Molen", 1)]
    },
    {
        "question": "Macam Tense Inggris",
        "answers": [("Perfect Tense", 1), ("Past Tense", 1), ("Present Tense", 1), ("Future Tense", 1)]
    },
    {
        "question": "Makanan Dengan Kandungan Karbohidrat",
        "answers": [("Nasi", 1), ("Roti", 1), ("Kentang", 1), ("Sagu", 1), ("Jagung", 1)]
    },
    {
        "question": "Mainan Apa Saja Yang Ada Di Dunia Fantasi",
        "answers": [("Halilintar", 1), ("Niagara", 1), ("Arung Jeram", 1), ("Kora Kora", 1), ("Pontang Panting", 1)]
    },
    {
        "question": "Makanan Khas Sulawesi",
        "answers": [("Buras", 1), ("Kapurung", 1), ("Barongkong", 1), ("Coto Makassar", 1), ("Pisang Ijo", 1)]
    },
    {
        "question": "Makanan Yang Termasuk Gorengan",
        "answers": [("Ubi", 1), ("Tahu", 1), ("Tempe", 1), ("Pisang", 1), ("Cireng", 1), ("Bakwan", 1)]
    },
    {
        "question": "Makanan Yang Ada Di Warteg",
        "answers": [("Rawon", 1), ("Soto", 1), ("Pecel", 1), ("Kari Ayam", 1), ("Sayur Lodeh", 1)]
    },
    {
        "question": "Mall Mall Gede Di Surabaya",
        "answers": [("Ciputra World", 1), ("Supermall Pakuwon Indah", 1), ("Tunjungan Plaza", 1), ("Galaxy Mall", 1), ("Lenmarc", 1), ("Grand City", 1)]
    },
    {
        "question": "Mata Air",
        "answers": [("Sungai", 1), ("Laut", 1), ("Danau", 1), ("Air Tanah", 1), ("Samudera", 1)]
    },
    {
        "question": "Mata Uang Yang Berawalan R",
        "answers": [("Rupiah", 1), ("Riyal", 1), ("Riel", 1), ("Rupee", 1), ("Ringgit", 1)]
    },
    {
        "question": "Media Komunikasi",
        "answers": [("Radio", 1), ("Telepon", 1), ("Fax", 1), ("Koran", 1), ("Tv", 1), ("Internet", 1)]
    },
    {
        "question": "Merk Gel Rambut",
        "answers": [("Gatsby", 1), ("Brisk", 1), ("Clear", 1)]
    },
    {
        "question": "Merk Tv",
        "answers": [("Politron", 1), ("Sony", 1), ("Panasonic", 1), ("Toshiba", 1), ("Samsung", 1), ("Sanken", 1)]
    },
    {
        "question": "Merek Baterai Di Indonesia",
        "answers": [("National", 1), ("ABC", 1), ("Energizer", 1), ("Eveready", 1), ("Panasonic", 1), ("Hitachi", 1)]
    },
    {
        "question": "Merk Coklat Yang Digemari",
        "answers": [("Silver Queen", 1), ("Toblerone", 1), ("Delfi", 1), ("Cadburry", 1)]
    },
    {
        "question": "Merk Hardisk",
        "answers": [("Quantum", 1), ("Seagate", 1), ("Maxtor", 1), ("Wdc", 1), ("Mdt", 1)]
    },
    {
        "question": "Merk Komputer",
        "answers": [("Toshiba", 1), ("Sony", 1), ("Fujitsu", 1), ("Ibm", 1), ("Panasonic", 1), ("Simba", 1), ("Nec", 1)]
    },
    {
        "question": "Merk Mobil Terkenal",
        "answers": [("Honda", 1), ("Mercedez", 1), ("Ferarri", 1), ("Bmw", 1), ("Jaguar", 1)]
    },
    {
        "question": "Mobil Keluaran Toyota",
        "answers": [("Harrier", 1), ("Land Cruiser", 1), ("Fortuner", 1), ("Camry", 1), ("Rush", 1)]
    },
    {
        "question": "Mobil Mini",
        "answers": [("Getz", 1), ("Jazz", 1), ("A Class", 1), ("Atoz", 1), ("Swift", 1), ("Karimun", 1), ("Ceria", 1)]
    },
    {
        "question": "Motor Bebek Keluaran Honda",
        "answers": [("Supra", 1), ("Kharisma", 1), ("Bebek 70", 1), ("Legenda", 1), ("Prima", 1), ("Astrea", 1)]
    },
    {
        "question": "Mobil Keluaran Honda",
        "answers": [("Stream", 1), ("Civic", 1), ("Cr-v", 1), ("Jazz", 1), ("City", 1)]
    },
    {
        "question": "Nama Bandara Indonesia",
        "answers": [("Ngurah Rai", 1), ("Soekarno Hatta", 1), ("Juanda", 1), ("Adi Sucipto", 1)]
    },
    {
        "question": "Nama Gurun",
        "answers": [("Sahara", 1), ("Gobi", 1), ("Victoria", 1), ("Thar", 1), ("Kalahari", 1)]
    },
    {
        "question": "Nama Hewan Berawalan A",
        "answers": [("Anjing", 1), ("Ayam", 1), ("Angsa", 1), ("Anjing Laut", 1)]
    },
    {
        "question": "Nama Nama Burung",
        "answers": [("Kutilang", 1), ("Beo", 1), ("Cendrawasih", 1), ("Elang", 1), ("Pipit", 1), ("Gagak", 1), ("Kakatua", 1)]
    },
    {
        "question": "Nama Nama Danau",
        "answers": [("Toba", 1), ("Gajah Mungkur", 1), ("Jatiluhur", 1)]
    },
    {
        "question": "Nama Pengarang Novel Terkenal Di Dunia",
        "answers": [("John Grisham", 1), ("Alfred Hitchcock", 1)]
    },
    {
        "question": "Nama Nama Restoran Impor",
        "answers": [("Cfc", 1), ("Pizza Hut", 1), ("Texas", 1), ("Dunkin Donut", 1), ("Kfc", 1)]
    },
    {
        "question": "Nama Negara Yang Punya Hak Veto Pbb Dalam Bahasa Inggris",
        "answers": [("China", 1), ("France", 1), ("USA", 1), ("Russia", 1), ("England", 1)]
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
