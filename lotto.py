"""로또 번호 생성기 — 버튼을 누르면 6개 숫자 x 5세트를 보여 줘요.

실행: conda activate camp → python lotto.py
(tkinter는 파이썬에 기본으로 들어 있어서 따로 설치할 게 없어요)
"""

import random
import tkinter as tk
from datetime import datetime

SETS = 5      # 몇 세트 뽑을지
PICKS = 6     # 한 세트에 숫자 몇 개
MAX_NUM = 45  # 1 ~ 45


def ball_color(n):
    """동행복권 공 색상: 1~10 노랑, 11~20 파랑, 21~30 빨강, 31~40 회색, 41~45 초록"""
    if n <= 10:
        return "#FBC400"
    if n <= 20:
        return "#69C8F2"
    if n <= 30:
        return "#FF7272"
    if n <= 40:
        return "#AAAAAA"
    return "#B0D840"


def draw_ball(canvas, x, y, n, r=22):
    """동그란 공 하나 그리기"""
    canvas.create_oval(x - r, y - r, x + r, y + r, fill=ball_color(n), outline="")
    canvas.create_text(x, y, text=str(n), fill="white", font=("맑은 고딕", 14, "bold"))


def generate():
    """버튼을 누르면 실행: 날짜 갱신 + 5세트 새로 뽑기"""
    now = datetime.now()
    weekdays = "월화수목금토일"
    date_label.config(
        text=now.strftime("%Y년 %m월 %d일 ") + f"({weekdays[now.weekday()]}) " + now.strftime("%H:%M:%S")
    )

    canvas.delete("all")
    for i in range(SETS):
        numbers = sorted(random.sample(range(1, MAX_NUM + 1), PICKS))  # 겹치지 않게 6개
        y = 40 + i * 60
        canvas.create_text(30, y, text=chr(ord("A") + i), font=("맑은 고딕", 14, "bold"), fill="#333")
        for j, n in enumerate(numbers):
            draw_ball(canvas, 80 + j * 55, y, n)


root = tk.Tk()
root.title("로또 번호 생성기")
root.resizable(False, False)
root.configure(bg="white")

tk.Label(root, text="🎱 로또 번호 생성기", font=("맑은 고딕", 18, "bold"), bg="white").pack(pady=(15, 5))
date_label = tk.Label(root, text="버튼을 눌러 번호를 뽑아 보세요", font=("맑은 고딕", 11), fg="#666", bg="white")
date_label.pack()

canvas = tk.Canvas(root, width=400, height=310, bg="white", highlightthickness=0)
canvas.pack(padx=15, pady=10)

tk.Button(
    root, text="번호 뽑기", font=("맑은 고딕", 13, "bold"),
    bg="#1E88E5", fg="white", activebackground="#1565C0", activeforeground="white",
    relief="flat", padx=20, pady=6, command=generate,
).pack(pady=(0, 15))

root.mainloop()
