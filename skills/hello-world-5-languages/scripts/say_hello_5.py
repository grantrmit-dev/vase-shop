#!/usr/bin/env python3
import random

GREETINGS = {
    "English": "Hello, world!",
    "Spanish": "¡Hola, mundo!",
    "French": "Bonjour, le monde !",
    "German": "Hallo, Welt!",
    "Italian": "Ciao, mondo!",
    "Portuguese": "Olá, mundo!",
    "Dutch": "Hallo, wereld!",
    "Swedish": "Hej, världen!",
    "Norwegian": "Hei, verden!",
    "Danish": "Hej, verden!",
    "Finnish": "Hei, maailma!",
    "Polish": "Witaj, świecie!",
    "Czech": "Ahoj, světe!",
    "Romanian": "Salut, lume!",
    "Turkish": "Merhaba, dünya!",
    "Arabic": "مرحبًا بالعالم!",
    "Hebrew": "שלום עולם!",
    "Hindi": "नमस्ते दुनिया!",
    "Bengali": "ওহে বিশ্ব!",
    "Chinese (Simplified)": "你好，世界！",
    "Chinese (Traditional)": "你好，世界！",
    "Japanese": "こんにちは、世界！",
    "Korean": "안녕, 세상!",
    "Thai": "สวัสดีชาวโลก!",
    "Vietnamese": "Xin chào, thế giới!",
    "Indonesian": "Halo, dunia!",
    "Malay": "Halo, dunia!",
    "Swahili": "Habari, dunia!",
    "Greek": "Γειά σου, κόσμε!",
    "Russian": "Привет, мир!",
    "Ukrainian": "Привіт, світе!"
}

for language in random.sample(list(GREETINGS.keys()), 5):
    print(f"{language}: {GREETINGS[language]}")
