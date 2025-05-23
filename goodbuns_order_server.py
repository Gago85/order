from flask import Flask, request, jsonify
from docx import Document
from flask_cors import CORS
from datetime import datetime
import os
import requests

app = Flask(__name__)
CORS(app)

TELEGRAM_TOKEN = "7714393507:AAGSwESX_TAT7_IYsJWAiUXhCge69thfG9Y"
CHAT_ID = "524359902"
SAVE_PATH = "D:/ЗАКАЗ КОФЙЕН СКЛАД"

def create_doc(data):
    date_str = datetime.now().strftime("%Y-%m-%d")
    point = data.get("point", "Не указано")
    day = data.get("day", "Не указано")
    items = data.get("items", [])

    folder = os.path.join(SAVE_PATH, date_str)
    os.makedirs(folder, exist_ok=True)

    filename = f"{date_str}_{point}_{day}.docx"
    filepath = os.path.join(folder, filename)

    doc = Document()
    doc.add_heading("ПРИХОДНАЯ НАКЛАДНАЯ", 0)
    doc.add_paragraph(f"Дата: {date_str}")
    doc.add_paragraph(f"Точка: {point}")
    doc.add_paragraph(f"День: {day}")
    doc.add_paragraph("")

    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Наименование"
    hdr_cells[1].text = "Количество"

    for item in items:
        name = item.get("name")
        qty = item.get("qty")
        if name and qty:
            row_cells = table.add_row().cells
            row_cells[0].text = name
            row_cells[1].text = str(qty)

    doc.add_paragraph("\nПринял: ____________________")
    doc.add_paragraph("Выдал: ____________________")
    doc.save(filepath)
    return filepath

def send_to_telegram(filepath):
    with open(filepath, "rb") as f:
        files = {'document': f}
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        data = {"chat_id": CHAT_ID, "caption": "🧾 Новый заказ"}
        response = requests.post(url, data=data, files=files)
        return response.ok

@app.route("/order", methods=["POST"])
def handle_order():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Нет данных"}), 400

    try:
        filepath = create_doc(data)
        sent = send_to_telegram(filepath)
        return jsonify({"status": "ok", "saved": filepath, "telegram_sent": sent}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
