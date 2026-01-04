import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SECRET_KEY = 'auto_grading_system_secret_key'
    
    # Data Paths
    DLL_PATH = os.path.join(BASE_DIR, 'build', 'libgrading.dll')
    DATA_FILE = os.path.join(BASE_DIR, 'questions.txt')
    RESULTS_FILE = os.path.join(BASE_DIR, 'results.json')
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'web', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
