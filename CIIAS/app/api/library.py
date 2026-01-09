from flask import Blueprint, request, jsonify
from app import db
from app.models import Book

library_bp = Blueprint('library', __name__)

@library_bp.route('/books', methods=['GET'])
def get_books():
    query = request.args.get('q')
    category = request.args.get('category')
    
    q = Book.query
    if query:
        search = f"%{query}%"
        q = q.filter((Book.title.like(search)) | (Book.author.like(search)))
    
    if category:
        q = q.filter_by(category=category)
        
    books = q.all()
    return jsonify([b.to_dict() for b in books]), 200

@library_bp.route('/loans/issue', methods=['POST'])
def issue_book():
    # Mock issue logic
    return jsonify({'message': 'Book issued successfully'}), 200
