from flask import Flask, render_template, request, redirect, url_for, flash
import os
import time
import glob
from services.planner_service import run_full_planning
from pipelines.input_pipeline import preprocess_input
from os.path import basename
# app.py
from flask import Flask, jsonify
from tkinter import filedialog, Tk
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'

PROMPT_DIR = 'prompts'
SAVED_PROMPT_DIR = 'saved_prompts'
os.makedirs(PROMPT_DIR, exist_ok=True)
os.makedirs(SAVED_PROMPT_DIR, exist_ok=True)

DEFAULT_PROMPT_FILE = os.path.join(PROMPT_DIR, 'prompt_template.txt')
current_prompt_file = None
state_dir = None

def get_latest_prompt_file():
    files = sorted(glob.glob(os.path.join(SAVED_PROMPT_DIR, '*.txt')), reverse=True)
    return files[0] if files else DEFAULT_PROMPT_FILE

def save_new_prompt(content):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    new_file_path = os.path.join(SAVED_PROMPT_DIR, f'prompt_{timestamp}.txt')
    with open(new_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return new_file_path

@app.route('/', methods=['GET', 'POST'])
def index():
    global state_dir, current_prompt_file

    if request.method == 'POST':
        file_path = request.form.get('log_path', '').strip()
        if not file_path or not os.path.exists(file_path):
            flash('Sếp ơi, đường dẫn không tồn tại hoặc bị bỏ trống')
            return redirect(url_for('index'))

        prompt_file = current_prompt_file if current_prompt_file else get_latest_prompt_file()
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()

        user_input = prompt_template.replace("{file_path}", file_path)
        processed_input = preprocess_input(user_input)
        _, state_dir = run_full_planning(processed_input)
        id_dir = os.path.basename(state_dir.rstrip(os.sep))

        return redirect(url_for('result', id_dir=id_dir))

    prompt_file = current_prompt_file if current_prompt_file else get_latest_prompt_file()
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_preview = f.read()

    return render_template('index.html', prompt=prompt_preview)


# @app.route('/result')
# def result():
#     global state_dir

#     result_text = ''
#     files = []

#     if state_dir:
#         log_path = os.path.join(state_dir, "message_notify_log.txt")
#         if os.path.exists(log_path):
#             with open(log_path, "r", encoding='utf-8') as f:
#                 result_text = f.read()
#         files = os.listdir(state_dir)
    
#     messages = []
#     if result_text:
#         # Tách chuỗi log thành các phần nhỏ, mỗi phần bắt đầu bằng "Message sent at:"
#         parts = result_text.split("Message sent at:")
#         for part in parts:
#             part = part.strip()
#             if part:
#                 messages.append("Message sent at: " + part)

#     return render_template('result.html', messages=messages, files=files)

@app.route('/result/<id_dir>')
def result(id_dir):
    state_dir = f"./test_environment/{id_dir}"
    result_text = ''
    files = []
    if state_dir:
        log_path = os.path.join(state_dir, "message_notify_log.txt")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding='utf-8') as f:
                result_text = f.read()
        files = os.listdir(state_dir)
    
    messages = []
    if result_text:
        # Tách chuỗi log thành các phần nhỏ, mỗi phần bắt đầu bằng "Message sent at:"
        parts = result_text.split("Message sent at:")
        for part in parts:
            part = part.strip()
            if part:
                messages.append("Message sent at: " + part)

    return render_template('result.html', messages=messages, files=files)

@app.route('/edit_prompt', methods=['GET', 'POST'])
def edit_prompt():
    latest_prompt_file = get_latest_prompt_file()

    if request.method == 'POST':
        new_prompt = request.form['prompt_text']
        save_new_prompt(new_prompt)
        flash('Đã lưu prompt mới!')
        return redirect(url_for('edit_prompt'))

    with open(latest_prompt_file, 'r', encoding='utf-8') as f:
        current_prompt = f.read()

    return render_template('edit_prompt.html', prompt=current_prompt)

@app.route('/prompts', methods=['GET', 'POST'])
def prompts():
    global current_prompt_file
    prompt_files = sorted(glob.glob(os.path.join(SAVED_PROMPT_DIR, '*.txt')), reverse=True)

    prompt_data = [{"path": path, "name": os.path.basename(path)} for path in prompt_files]

    if request.method == 'POST':
        selected_file = request.form.get('selected_prompt')
        if selected_file and os.path.exists(selected_file):
            current_prompt_file = selected_file
            flash(f'Đã chọn prompt: {os.path.basename(selected_file)}')

    return render_template('prompt_list.html', prompts=prompt_data, current=current_prompt_file)

@app.route('/view_prompt/<filename>')
def view_prompt(filename):
    file_path = os.path.join(SAVED_PROMPT_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return f"<h3>{filename}</h3><pre>{content}</pre>"

@app.route('/upload', methods=['POST'])
def upload():
    if 'logfile' not in request.files:
        return "Chưa chọn file"
    file = request.files['logfile']
    if file.filename == '':
        return "Không có file được chọn"
    file_name = file.filename
    # Nếu bạn muốn lưu file lên server:
    # file.save(os.path.join('uploads', file_name))

    return f"File bạn chọn là: {file_name}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2025, debug=True)
