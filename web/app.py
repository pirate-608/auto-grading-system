import os
import ctypes
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'auto_grading_system_secret_key'  # 设置 Secret Key 以启用 Session

@app.after_request
def add_header(response):
    # 尝试解决 ngrok 免费版拦截页面问题 (主要针对 API 调用或特定客户端)
    response.headers['ngrok-skip-browser-warning'] = 'true'
    # 防止浏览器缓存页面 (对于考试页面很重要)
    if 'exam' in request.path:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

@app.before_request
def check_exam_mode():
    # 如果用户处于考试模式
    if session.get('in_exam'):
        # 允许访问的端点：exam (考试页), static (静态资源)
        # 注意：request.endpoint 在请求静态文件时可能是 'static'
        if request.endpoint in ['exam', 'static']:
            return
        # 其他页面一律重定向回考试页
        flash('考试进行中，无法访问其他页面！', 'warning')
        return redirect(url_for('exam'))

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DLL_PATH = os.path.join(BASE_DIR, 'build', 'libgrading.dll')
DATA_FILE = os.path.join(BASE_DIR, 'questions.txt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'web', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load C Library
try:
    lib = ctypes.CDLL(DLL_PATH)
    # int calculate_score(const char* user_ans, const char* correct_ans, int full_score);
    lib.calculate_score.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    lib.calculate_score.restype = ctypes.c_int
    print(f"Successfully loaded DLL from {DLL_PATH}")
except Exception as e:
    print(f"Error loading DLL: {e}")
    lib = None

def load_questions():
    questions = []
    if not os.path.exists(DATA_FILE):
        return questions
    
    lines = []
    try:
        # Try UTF-8 first (standard)
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            # Try GB18030 (superset of GBK, common on Windows CN)
            with open(DATA_FILE, 'r', encoding='gb18030') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Fallback with replacement to avoid crash
            with open(DATA_FILE, 'r', encoding='gb18030', errors='replace') as f:
                lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line: continue
        parts = line.split('|')
        if len(parts) >= 3:
            try:
                q = {
                    'content': parts[0],
                    'answer': parts[1],
                    'score': int(parts[2]),
                    'image': ''
                }
                if len(parts) >= 4:
                    q['image'] = parts[3]
                questions.append(q)
            except ValueError:
                continue
    return questions

def save_question(content, answer, score, image=''):
    # Append with newline
    with open(DATA_FILE, 'a', encoding='utf-8') as f: # Use UTF-8 for consistency
        f.write(f"\n{content}|{answer}|{score}|{image}")

def save_all_questions(questions):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        for i, q in enumerate(questions):
            image = q.get('image', '')
            line = f"{q['content']}|{q['answer']}|{q['score']}|{image}"
            if i < len(questions) - 1:
                line += "\n"
            f.write(line)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manage')
def manage():
    questions = load_questions()
    return render_template('manage.html', questions=questions)

@app.route('/delete/<int:index>', methods=['POST'])
def delete_question(index):
    questions = load_questions()
    if 0 <= index < len(questions):
        q = questions.pop(index)
        # Delete image file if exists
        if q.get('image'):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], q['image'])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except:
                    pass
        save_all_questions(questions)
    return redirect(url_for('manage'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_question(index):
    questions = load_questions()
    if not (0 <= index < len(questions)):
        return redirect(url_for('manage'))
    
    if request.method == 'POST':
        content = request.form.get('content')
        answer = request.form.get('answer')
        score = request.form.get('score')
        
        if content and answer and score:
            image_filename = questions[index].get('image', '')
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    # Delete old image if exists
                    if image_filename:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                        if os.path.exists(old_image_path):
                            try:
                                os.remove(old_image_path)
                            except:
                                pass
                                
                    filename = secure_filename(file.filename)
                    # Generate unique filename to avoid collision
                    unique_filename = str(uuid.uuid4()) + "_" + filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    image_filename = unique_filename

            questions[index] = {
                'content': content,
                'answer': answer,
                'score': int(score),
                'image': image_filename
            }
            save_all_questions(questions)
            return redirect(url_for('manage'))
            
    return render_template('edit.html', question=questions[index], index=index)

@app.route('/start_exam')
def start_exam():
    session['in_exam'] = True
    return redirect(url_for('exam'))

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    # 如果未开始考试且尝试访问考试页，重定向回首页
    if not session.get('in_exam') and request.method == 'GET':
        return redirect(url_for('index'))

    questions = load_questions()
    if request.method == 'POST':
        total_score = 0
        results = []
        
        for i, q in enumerate(questions):
            user_ans = request.form.get(f'q_{i}', '')
            
            # Support multiple valid answers separated by ; or ；
            valid_answers = q['answer'].replace('；', ';').split(';')
            valid_answers = [ans.strip() for ans in valid_answers if ans.strip()]
            if not valid_answers:
                valid_answers = [q['answer']] # Fallback if split results in empty

            score = 0
            # Check against all valid answers and take the max score
            for correct_ans in valid_answers:
                current_score = 0
                # Use C function for grading if available
                if lib:
                    # Encode strings to bytes for C (GBK for Windows C app compatibility usually)
                    # But grading.c uses tolower which works on ASCII. 
                    # If Chinese characters are involved, simple byte comparison works if encoding matches.
                    try:
                        b_user = user_ans.encode('gbk')
                        b_correct = correct_ans.encode('gbk')
                    except:
                        b_user = user_ans.encode('utf-8')
                        b_correct = correct_ans.encode('utf-8')
                        
                    current_score = lib.calculate_score(b_user, b_correct, q['score'])
                else:
                    # Fallback python implementation
                    current_score = q['score'] if user_ans.strip().lower() == correct_ans.strip().lower() else 0
                
                if current_score > score:
                    score = current_score
            
            total_score += score
            results.append({
                'question': q['content'],
                'user_ans': user_ans,
                'correct_ans': q['answer'], # Show original full answer string
                'score': score,
                'full_score': q['score']
            })
        
        # 考试结束，清除会话状态
        session.pop('in_exam', None)
        return render_template('result.html', total_score=total_score, results=results)
    
    return render_template('exam.html', questions=questions)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Handle list of values
        contents = request.form.getlist('content[]')
        answers = request.form.getlist('answer[]')
        scores = request.form.getlist('score[]')
        images = request.files.getlist('image[]')
        
        # If single item (old form style or single entry), getlist still works if name matches
        # If names were different, we'd need fallback. But we updated the template.
        
        if contents and answers and scores:
            # Ensure images list matches length of other lists (it might not if empty inputs are not sent)
            # Actually, file inputs always send a part, even if empty. So length should match.
            
            for i, (c, a, s) in enumerate(zip(contents, answers, scores)):
                if c and a and s:
                    image_filename = ''
                    if i < len(images):
                        file = images[i]
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            unique_filename = str(uuid.uuid4()) + "_" + filename
                            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                            image_filename = unique_filename
                            
                    save_question(c, a, s, image_filename)
            return redirect(url_for('index'))
            
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
