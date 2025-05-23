from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from docx import Document
import os
import requests

app = Flask(__name__)
CORS(app)

# Главная страница
@app.route("/", methods=["GET"])
def home():
    return "Сервер работает. Для отправки заказов используйте /order"

# Создание Word-документа
def create_doc(data):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H-%M-%S")
    filename = f"Приходная накладная - {date_str}.docx"
    filepath = os.path.join("/tmp", filename)

    doc = Document()
    doc.add_heading("Приходная накладная", level=1)
    doc.add_paragraph(f"Дата и время: {date_str}")
    doc.add_paragraph(f"Точка: {data.get('point', 'Не указано')}")
    doc.add_paragraph(f"День недели: {data.get('day', 'Не указано')}")
    doc.add_paragraph("")

    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Наименование'
    hdr_cells[1].text = 'Количество'

    for item in data.get("items", []):
        row_cells = table.add_row().cells
        row_cells[0].text = item.get("name", "")
        row_cells[1].text = str(item.get("qty", ""))

    doc.save(filepath)
    return filepath

# Отправка документа в Telegram
def send_to_telegram(filepath):
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    with open(filepath, 'rb') as doc_file:
        files = {'document': doc_file}
        data = {'chat_id': chat_id}
        response = requests.post(url, files=files, data=data)

    return response.status_code == 200

# Прием заказов
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

