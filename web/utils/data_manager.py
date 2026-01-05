import os
import json
import shutil
from datetime import datetime
from models import db, Question, ExamResult, User

class DataManager:
    def __init__(self, config):
        self.config = config
        self._ensure_directories()
        self._check_legacy_db()

    def _ensure_directories(self):
        if not os.path.exists(self.config.UPLOAD_FOLDER):
            os.makedirs(self.config.UPLOAD_FOLDER)
        if hasattr(self.config, 'INSTANCE_PATH') and not os.path.exists(self.config.INSTANCE_PATH):
            os.makedirs(self.config.INSTANCE_PATH)

    def _check_legacy_db(self):
        # Move data.db from root to instance folder if it exists in root and not in instance
        old_db = os.path.join(self.config.BASE_DIR, 'data.db')
        new_db = os.path.join(self.config.INSTANCE_PATH, 'data.db')
        if os.path.exists(old_db) and not os.path.exists(new_db):
            print(f"Moving legacy database from {old_db} to {new_db}")
            try:
                shutil.move(old_db, new_db)
            except Exception as e:
                print(f"Error moving database: {e}")

    def init_db(self, app):
        """Initialize database and migrate data if empty"""
        with app.app_context():
            db.create_all()
            if Question.query.count() == 0:
                self.migrate_from_files()
            
            # Create default admin if not exists
            if User.query.filter_by(username='admin').first() is None:
                admin = User(username='admin', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Created default admin user (admin/admin123)")

    def migrate_from_files(self):
        print("Migrating data from files to SQLite...")
        # Migrate Questions
        if os.path.exists(self.config.DATA_FILE):
            try:
                with open(self.config.DATA_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    parts = line.split('|')
                    if len(parts) >= 3:
                        content = parts[0].replace('[NEWLINE]', '\n')
                        answer = parts[1]
                        score = int(parts[2])
                        image = parts[3] if len(parts) >= 4 else ''
                        category = parts[4] if len(parts) >= 5 else '默认题集'
                        
                        q = Question(content=content, answer=answer, score=score, image=image, category=category)
                        db.session.add(q)
                db.session.commit()
                print("Questions migrated.")
            except Exception as e:
                print(f"Error migrating questions: {e}")

        # Migrate Results
        if os.path.exists(self.config.RESULTS_FILE):
            try:
                with open(self.config.RESULTS_FILE, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                for r in results:
                    result = ExamResult(
                        id=r['id'],
                        timestamp=r['timestamp'],
                        total_score=r['total_score'],
                        max_score=r['max_score']
                    )
                    result.details = r['details']
                    db.session.add(result)
                db.session.commit()
                print("Results migrated.")
            except Exception as e:
                print(f"Error migrating results: {e}")

    def load_questions(self):
        questions = Question.query.order_by(Question.id).all()
        return [q.to_dict() for q in questions]

    def get_question(self, q_id):
        q = Question.query.get(q_id)
        return q.to_dict() if q else None

    def save_question(self, content, answer, score, image='', category='默认题集'):
        q = Question(content=content, answer=answer, score=score, image=image, category=category)
        db.session.add(q)
        db.session.commit()

    def update_question(self, q_id, content, answer, score, image=None, category=None):
        q = Question.query.get(q_id)
        if q:
            q.content = content
            q.answer = answer
            q.score = score
            if image is not None:
                q.image = image
            if category is not None:
                q.category = category
            db.session.commit()

    def delete_question(self, q_id):
        q = Question.query.get(q_id)
        if q:
            db.session.delete(q)
            db.session.commit()
            return q.image
        return None

    # Deprecated but kept for compatibility if needed (though we should avoid using it)
    def save_all_questions(self, questions):
        # This is hard to map to DB efficiently without IDs.
        # We will avoid using this in the new app.py
        pass

    def get_questions_paginated(self, page=1, per_page=10, search=None, category=None):
        query = Question.query
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Question.content.like(search_term)) | 
                (Question.category.like(search_term))
            )
        if category and category != 'all':
            query = query.filter_by(category=category)
        
        return query.order_by(Question.id.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def get_system_stats(self):
        total_questions = Question.query.count()
        total_exams = ExamResult.query.count()
        
        # Calculate average score
        from sqlalchemy import func
        avg_score = db.session.query(func.avg(ExamResult.total_score)).scalar()
        avg_score = round(avg_score, 1) if avg_score else 0
        
        return {
            'total_questions': total_questions,
            'total_exams': total_exams,
            'avg_score': avg_score
        }

    def get_categories(self):
        # Use distinct query
        categories = db.session.query(Question.category).distinct().all()
        return sorted([c[0] for c in categories if c[0]])

    def load_results(self, user_id=None):
        query = ExamResult.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        results = query.order_by(ExamResult.timestamp.desc()).all()
        return [r.to_dict() for r in results]

    def save_exam_result(self, result_dict, user_id=None):
        result = ExamResult(
            id=result_dict['id'],
            timestamp=result_dict['timestamp'],
            total_score=result_dict['total_score'],
            max_score=result_dict['max_score'],
            user_id=user_id
        )
        result.details = result_dict['details']
        db.session.add(result)
        db.session.commit()

    def get_result(self, result_id):
        r = ExamResult.query.get(result_id)
        return r.to_dict() if r else None

    def delete_result(self, result_id):
        r = ExamResult.query.get(result_id)
        if r:
            db.session.delete(r)
            db.session.commit()

    def create_user(self, username, password, is_admin=False):
        if User.query.filter_by(username=username).first():
            return False
        user = User(username=username, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return True

    def get_user_dashboard_stats(self, user_id):
        # 1. Score Trend (Last 7 exams)
        recent_exams = ExamResult.query.filter_by(user_id=user_id)\
            .order_by(ExamResult.timestamp.desc())\
            .limit(7).all()
        recent_exams.reverse() # Make it chronological
        
        trend_labels = [r.timestamp.split(' ')[0] for r in recent_exams]
        trend_data = [r.total_score for r in recent_exams]
        
        # 2. Error Analysis (Top 5 wrong questions from last 20 exams)
        analyze_exams = ExamResult.query.filter_by(user_id=user_id)\
            .order_by(ExamResult.timestamp.desc())\
            .limit(20).all()
            
        question_stats = {} # {short_content: {wrong: 0, total: 0}}
        
        for exam in analyze_exams:
            details = exam.details
            if not details: continue
            for q in details:
                content = q.get('question')
                if not content: continue
                
                # Truncate content
                short_content = (content[:10] + '..') if len(content) > 10 else content
                
                if short_content not in question_stats:
                    question_stats[short_content] = {'wrong': 0, 'total': 0}
                
                question_stats[short_content]['total'] += 1
                if q.get('score', 0) < q.get('full_score', 0):
                    question_stats[short_content]['wrong'] += 1
                    
        # Calculate error counts
        error_list = []
        for content, stats in question_stats.items():
            if stats['wrong'] > 0:
                error_list.append({'label': content, 'count': stats['wrong']})
        
        # Sort by error count descending
        error_list.sort(key=lambda x: x['count'], reverse=True)
        top_errors = error_list[:5]
        
        return {
            'trend': {
                'labels': trend_labels,
                'data': trend_data
            },
            'errors': {
                'labels': [x['label'] for x in top_errors],
                'data': [x['count'] for x in top_errors]
            }
        }

