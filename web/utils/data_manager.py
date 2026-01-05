import os
import json
import shutil
from datetime import datetime

class DataManager:
    def __init__(self, config):
        self.config = config
        self._ensure_directories()

    def _ensure_directories(self):
        if not os.path.exists(self.config.UPLOAD_FOLDER):
            os.makedirs(self.config.UPLOAD_FOLDER)

    def backup_data(self):
        """Backup questions file before writing"""
        if os.path.exists(self.config.DATA_FILE):
            backup_path = self.config.DATA_FILE + '.bak'
            try:
                shutil.copy2(self.config.DATA_FILE, backup_path)
            except Exception as e:
                print(f"Backup failed: {e}")

    def load_questions(self):
        questions = []
        if not os.path.exists(self.config.DATA_FILE):
            return questions
        
        lines = []
        try:
            with open(self.config.DATA_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(self.config.DATA_FILE, 'r', encoding='gb18030') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(self.config.DATA_FILE, 'r', encoding='gb18030', errors='replace') as f:
                    lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line: continue
            parts = line.split('|')
            if len(parts) >= 3:
                try:
                    q = {
                        'content': parts[0].replace('[NEWLINE]', '\n'),
                        'answer': parts[1],
                        'score': int(parts[2]),
                        'image': '',
                        'category': '默认题集' # Default category
                    }
                    if len(parts) >= 4:
                        q['image'] = parts[3]
                    if len(parts) >= 5:
                        q['category'] = parts[4]
                    questions.append(q)
                except ValueError:
                    continue
        return questions

    def save_question(self, content, answer, score, image='', category='默认题集'):
        self.backup_data()
        # Escape newlines
        content = content.replace('\r\n', '\n').replace('\n', '[NEWLINE]')
        with open(self.config.DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}|{answer}|{score}|{image}|{category}")

    def save_all_questions(self, questions):
        self.backup_data()
        with open(self.config.DATA_FILE, 'w', encoding='utf-8') as f:
            for i, q in enumerate(questions):
                image = q.get('image', '')
                category = q.get('category', '默认题集')
                content = q['content'].replace('\r\n', '\n').replace('\n', '[NEWLINE]')
                line = f"{content}|{q['answer']}|{q['score']}|{image}|{category}"
                if i < len(questions) - 1:
                    line += "\n"
                f.write(line)

    def get_categories(self):
        questions = self.load_questions()
        categories = set(q.get('category', '默认题集') for q in questions)
        return sorted(list(categories))

    def load_results(self):
        if not os.path.exists(self.config.RESULTS_FILE):
            return []
        try:
            with open(self.config.RESULTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_results(self, results):
        with open(self.config.RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
