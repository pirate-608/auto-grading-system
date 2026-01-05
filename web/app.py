import os
import ctypes
import uuid
import json
import random
import csv
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from config import Config
from utils.data_manager import DataManager

app = Flask(__name__)
app.config.from_object(Config)
data_manager = DataManager(Config)

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Load C Library
try:
    lib = ctypes.CDLL(Config.DLL_PATH)
    # int calculate_score(const char* user_ans, const char* correct_ans, int full_score);
    lib.calculate_score.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
    lib.calculate_score.restype = ctypes.c_int
    print(f"Successfully loaded DLL from {Config.DLL_PATH}")
except Exception as e:
    print(f"Error loading DLL: {e}")
    lib = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manage')
def manage():
    questions = data_manager.load_questions()
    return render_template('manage.html', questions=questions)

@app.route('/delete/<int:index>', methods=['POST'])
def delete_question(index):
    questions = data_manager.load_questions()
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
        data_manager.save_all_questions(questions)
    return redirect(url_for('manage'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_question(index):
    questions = data_manager.load_questions()
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
                'image': image_filename,
                'category': request.form.get('category', '默认题集')
            }
            data_manager.save_all_questions(questions)
            return redirect(url_for('manage'))
            
    return render_template('edit.html', question=questions[index], index=index, categories=data_manager.get_categories())

@app.route('/select_set')
def select_set():
    questions = data_manager.load_questions()
    if not questions:
        flash('题库为空，请先添加题目！', 'warning')
        return redirect(url_for('index'))
        
    # Count questions per category
    categories = {}
    for q in questions:
        cat = q.get('category', '默认题集')
        categories[cat] = categories.get(cat, 0) + 1
        
    return render_template('select_set.html', categories=categories, total_count=len(questions))

@app.route('/start_exam')
def start_exam():
    # Redirect to selection page first
    return redirect(url_for('select_set'))

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    # Check if category is selected via GET param (first entry)
    category = request.args.get('category')
    
    # If starting new exam
    if request.method == 'GET' and not session.get('in_exam'):
        if not category:
            return redirect(url_for('select_set'))
        session['in_exam'] = True
        session['start_time'] = datetime.now().timestamp()
        session['exam_category'] = category # Store selected category

    # Security check
    if not session.get('in_exam'):
        return redirect(url_for('index'))

    all_questions = data_manager.load_questions()
    
    # Filter questions based on session category
    current_category = session.get('exam_category', 'all')
    if current_category != 'all':
        # We need to map filtered indices back to original indices for grading
        # Or just store the filtered questions in session? 
        # Better: Store original indices of the filtered questions
        filtered_indices = [i for i, q in enumerate(all_questions) if q.get('category', '默认题集') == current_category]
    else:
        filtered_indices = list(range(len(all_questions)))

    if not filtered_indices:
        session.pop('in_exam', None)
        flash('该题集没有题目！', 'warning')
        return redirect(url_for('select_set'))

    if request.method == 'GET':
        # Shuffle the filtered indices
        random.shuffle(filtered_indices)
        session['exam_indices'] = filtered_indices
        
        shuffled_questions = [all_questions[i] for i in filtered_indices]
        
        # Calculate remaining time
        start_time = session.get('start_time', datetime.now().timestamp())
        duration_sec = app.config['EXAM_DURATION_MINUTES'] * 60
        elapsed = datetime.now().timestamp() - start_time
        remaining_sec = max(0, int(duration_sec - elapsed))
        
        return render_template('exam.html', questions=shuffled_questions, remaining_sec=remaining_sec)

    if request.method == 'POST':
        # 获取随机化后的索引
        indices = session.get('exam_indices')
        if not indices:
             # Fallback if session lost
             return redirect(url_for('index'))
             
        questions = all_questions # Use full list, indices point to this
        
        total_score = 0
        results = []
        
        # 遍历提交的答案 (q_0, q_1, ...)
        # 注意：前端显示的第 i 题，对应的是 indices[i] 指向的原始题目
        for i, q_index in enumerate(indices):
            if q_index >= len(questions): continue # 防止越界
            
            q = questions[q_index]
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
        
        # Save result to history
        max_score = sum(q['score'] for q in questions)
        exam_record = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_score': total_score,
            'max_score': max_score,
            'details': results
        }
        all_results = data_manager.load_results()
        all_results.append(exam_record)
        data_manager.save_results(all_results)

        # 考试结束，清除会话状态
        session.pop('in_exam', None)
        session.pop('exam_indices', None)
        return render_template('result.html', total_score=total_score, results=results)
    
    return redirect(url_for('index'))

@app.route('/history')
def history():
    results = data_manager.load_results()
    # Sort by timestamp descending
    results.sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('history.html', results=results)

@app.route('/export_history')
def export_history():
    results = data_manager.load_results()
    # Sort by timestamp descending
    results.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['时间', '得分', '满分', '得分率'])
    
    for r in results:
        score = r.get('total_score', 0)
        max_s = r.get('max_score', 0)
        percentage = f"{(score / max_s * 100):.1f}%" if max_s > 0 else "0.0%"
        writer.writerow([r['timestamp'], score, max_s, percentage])
        
    output.seek(0)
    
    return Response(
        output.getvalue().encode('utf-8-sig'), # BOM for Excel
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=exam_history.csv"}
    )

@app.route('/history/delete/<result_id>', methods=['POST'])
def delete_history(result_id):
    results = data_manager.load_results()
    results = [r for r in results if r['id'] != result_id]
    data_manager.save_results(results)
    flash('记录已删除', 'success')
    return redirect(url_for('history'))

@app.route('/history/view/<result_id>')
def view_history(result_id):
    results = data_manager.load_results()
    record = next((r for r in results if r['id'] == result_id), None)
    if not record:
        flash('记录未找到', 'error')
        return redirect(url_for('history'))
    return render_template('result.html', total_score=record['total_score'], results=record['details'], is_history=True)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Handle list of values
        contents = request.form.getlist('content[]')
        answers = request.form.getlist('answer[]')
        scores = request.form.getlist('score[]')
        categories = request.form.getlist('category[]')
        images = request.files.getlist('image[]')
        
        if contents and answers and scores:
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
                    
                    cat = categories[i] if i < len(categories) and categories[i] else '默认题集'
                    data_manager.save_question(c, a, int(s), image_filename, cat)
            
            flash('题目添加成功！', 'success')
            return redirect(url_for('manage'))
            
    return render_template('add.html', categories=data_manager.get_categories())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
