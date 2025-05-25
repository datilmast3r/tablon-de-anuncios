from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load database configuration from .env
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT', '3306') # Default MySQL/MariaDB port

# Construct the SQLAlchemy Database URI for MySQL
# Format: mysql+pymysql://user:password@host:port/dbname
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppress a warning

db = SQLAlchemy(app)

# Define the Post model
class Post(db.Model):
    __tablename__ = 'posts'  # Explicitly set table name to match schema

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False) # Using db.Text for potentially longer messages
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@app.route('/posts', methods=['GET'])
def get_posts():
    """Retrieves all posts."""
    all_posts = Post.query.order_by(Post.created_at.desc()).all() # Order by creation time, newest first
    return jsonify([post.to_dict() for post in all_posts])

@app.route('/posts', methods=['POST'])
def add_post():
    """Adds a new post."""
    data = request.get_json()
    if not data or 'user_name' not in data or 'message' not in data:
        return jsonify({'error': 'user_name and message fields are required'}), 400

    user_name = data['user_name']
    message_text = data['message']

    if not user_name.strip() or not message_text.strip():
        return jsonify({'error': 'user_name and message cannot be empty'}), 400

    new_post_obj = Post(user_name=user_name, message=message_text)
    db.session.add(new_post_obj)
    db.session.commit()
    return jsonify(new_post_obj.to_dict()), 201

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)