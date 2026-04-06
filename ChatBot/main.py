import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
import json
import random

# ---------------- LOAD INTENTS ----------------
with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)

user_name = None

# ---------------- BOT LOGIC ----------------
def get_user_name(message):
    global user_name
    message = message.lower()

    if "my name is" in message:
        user_name = message.split("my name is")[-1].strip().title()
        return f"Nice to meet you, {user_name}!"

    elif "i am" in message:
        user_name = message.split("i am")[-1].strip().title()
        return f"Got it! I'll remember your name, {user_name}."

    elif "call me" in message:
        user_name = message.split("call me")[-1].strip().title()
        return f"Okay {user_name}, I will remember your name!"

    return None


def match_intent(user_input):
    user_input = user_input.lower()

    best_match = None
    best_score = 0

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            pattern_words = pattern.lower().split()
            score = sum(1 for word in pattern_words if word in user_input)

            # pick highest matching score
            if score > best_score:
                best_score = score
                best_match = intent

    return best_match, best_score


def get_response(user_input):
    global user_name

    # Check name first
    name_response = get_user_name(user_input)
    if name_response:
        return name_response

    intent, score = match_intent(user_input)

    # ✅ Threshold to avoid wrong matches
    if intent and score > 0:
        response = random.choice(intent["responses"])
    else:
        # fallback only if no match
        fallback = next(i for i in data["intents"] if i["tag"] == "fallback")
        response = random.choice(fallback["responses"])

    # Replace name if needed
    if "{name}" in response:
        response = response.replace("{name}", user_name if user_name else "there")

    return response


# ---------------- TKINTER UI ----------------
root = tk.Tk()
root.title("AI ChatBot Pro")
root.geometry("900x650")
root.configure(bg="#0d2818")

# HEADER
header = tk.Frame(root, bg="#1a4d2e", height=60)
header.pack(fill=tk.X)

title = tk.Label(header, text="🤖 AI ChatBot Pro", fg="white",
                 bg="#1a4d2e", font=("Segoe UI", 16, "bold"))
title.pack(side=tk.LEFT, padx=15)

status = tk.Label(header, text="● Online", fg="#4ade80",
                  bg="#1a4d2e", font=("Segoe UI", 10))
status.pack(side=tk.RIGHT, padx=15)

# CHAT AREA
chat_frame = tk.Frame(root, bg="#0d2818")
chat_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(chat_frame, bg="#0d2818", highlightthickness=0)
scrollbar = ttk.Scrollbar(chat_frame, orient="vertical", command=canvas.yview)

scrollable_frame = tk.Frame(canvas, bg="#0d2818")
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# MESSAGE BUBBLE
def add_message(message, sender="bot"):
    frame = tk.Frame(scrollable_frame, bg="#0d2818")

    time_label = tk.Label(
        frame,
        text=datetime.now().strftime("%H:%M"),
        font=("Segoe UI", 8),
        fg="#86efac",
        bg="#0d2818"
    )

    if sender == "user":
        bubble = tk.Label(
            frame,
            text=message,
            bg="#10b981",
            fg="white",
            font=("Segoe UI", 11),
            wraplength=500,
            justify="left",
            padx=10,
            pady=6
        )
        bubble.pack(anchor="e", padx=10)
        time_label.pack(anchor="e", padx=10)

    else:
        bubble = tk.Label(
            frame,
            text=message,
            bg="#1a4d2e",
            fg="white",
            font=("Segoe UI", 11),
            wraplength=500,
            justify="left",
            padx=10,
            pady=6
        )
        bubble.pack(anchor="w", padx=10)
        time_label.pack(anchor="w", padx=10)

    frame.pack(fill=tk.X, pady=5)
    canvas.update_idletasks()
    canvas.yview_moveto(1)

# BOT RESPONSE
def bot_response(user_input):
    typing_label = tk.Label(
        scrollable_frame,
        text="🤖 Typing...",
        fg="#86efac",
        bg="#0d2818",
        font=("Segoe UI", 10, "italic")
    )
    typing_label.pack(anchor="w", padx=10)

    canvas.update_idletasks()
    canvas.yview_moveto(1)

    time.sleep(1)
    typing_label.destroy()

    response = get_response(user_input)
    add_message("🤖 " + response, "bot")

# SEND MESSAGE
def send_message(event=None):
    user_input = entry.get().strip()

    if not user_input:
        return

    add_message("👤 " + user_input, "user")
    entry.delete(0, tk.END)

    threading.Thread(target=bot_response, args=(user_input,)).start()

# INPUT AREA
input_frame = tk.Frame(root, bg="#051912")
input_frame.pack(fill=tk.X, pady=10)

entry = tk.Entry(
    input_frame,
    font=("Segoe UI", 13),
    bg="#1a4d2e",
    fg="white",
    insertbackground="white",
    bd=0
)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=10)
entry.bind("<Return>", send_message)

send_btn = tk.Button(
    input_frame,
    text="➤",
    font=("Segoe UI", 14, "bold"),
    bg="#22c55e",
    fg="white",
    bd=0,
    padx=20,
    pady=8,
    command=send_message
)
send_btn.pack(side=tk.RIGHT, padx=10)

# WELCOME MESSAGE
add_message("🤖 Hello! I'm your AI assistant. Ask anything.", "bot")

root.mainloop()