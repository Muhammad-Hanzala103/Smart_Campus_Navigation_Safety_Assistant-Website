from flask import Blueprint, request, jsonify
from app import db
from app.models import Book
from app.utils import token_required

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

@library_bp.route('/borrow', methods=['POST'])
@token_required
def borrow_book(current_user):
    data = request.get_json()
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'error': 'Book ID required'}), 400
        
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
        
    if book.status != 'Available':
        return jsonify({'error': 'Book is not available'}), 400
        
    # In a real app, we would create a Loan record here
    book.status = 'Issued'
    db.session.commit()
    
    return jsonify({
        'message': 'Book borrowed successfully',
        'book': book.to_dict()
    }), 200
