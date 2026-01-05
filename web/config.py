import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SECRET_KEY = 'auto_grading_system_secret_key'
    
    # Data Paths
    DLL_PATH = os.path.join(BASE_DIR, 'build', 'libgrading.dll')
    DATA_FILE = os.path.join(BASE_DIR, 'questions.txt')
    RESULTS_FILE = os.path.join(BASE_DIR, 'results.json')
    
    # Database config
    WEB_DIR = os.path.dirname(os.path.abspath(__file__))
    INSTANCE_PATH = os.path.join(WEB_DIR, 'instance')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_PATH, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'web', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

    # Exam Settings
    EXAM_DURATION_MINUTES = 60  # 考试时长（分钟）
