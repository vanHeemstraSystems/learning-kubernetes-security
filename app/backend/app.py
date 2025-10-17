from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration from environment variables

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'postgres-service'),
    'database': os.environ.get('DB_NAME', 'notesdb'),
    'user': os.environ.get('DB_USER', 'notesuser'),
    'password': os.environ.get('DB_PASSWORD', 'changeme')
}

def get_db_connection():
    """Create database connection with error handling"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database schema"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create notes table if it doesn't exist
        cur.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for better query performance
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_notes_category 
            ON notes(category)
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Don't raise the exception - table might already exist
        pass

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check endpoint"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({'status': 'ready'}), 200
    except Exception as e:
        return jsonify({'status': 'not ready', 'error': str(e)}), 503

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Retrieve all notes or filter by category"""
    category = request.args.get('category')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if category:
            cur.execute(
                "SELECT id, title, content, category, created_at, updated_at FROM notes WHERE category = %s ORDER BY created_at DESC",
                (category,)
            )
        else:
            cur.execute(
                "SELECT id, title, content, category, created_at, updated_at FROM notes ORDER BY created_at DESC"
            )
        
        notes = []
        for row in cur.fetchall():
            notes.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None
            })
        
        cur.close()
        conn.close()
        
        return jsonify(notes), 200
    except Exception as e:
        logger.error(f"Error retrieving notes: {e}")
        return jsonify({'error': 'Failed to retrieve notes'}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Retrieve a specific note by ID"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "SELECT id, title, content, category, created_at, updated_at FROM notes WHERE id = %s",
            (note_id,)
        )
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            note = {
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'category': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None
            }
            return jsonify(note), 200
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        logger.error(f"Error retrieving note: {e}")
        return jsonify({'error': 'Failed to retrieve note'}), 500

@app.route('/api/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400
    
    title = data['title']
    content = data['content']
    category = data.get('category', 'general')
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO notes (title, content, category) VALUES (%s, %s, %s) RETURNING id",
            (title, content, category)
        )
        
        note_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'message': 'Note created successfully',
            'id': note_id
        }), 201
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        return jsonify({'error': 'Failed to create note'}), 500

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update an existing note"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        if 'title' in data:
            update_fields.append("title = %s")
            values.append(data['title'])
        if 'content' in data:
            update_fields.append("content = %s")
            values.append(data['content'])
        if 'category' in data:
            update_fields.append("category = %s")
            values.append(data['category'])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(note_id)
        
        query = f"UPDATE notes SET {', '.join(update_fields)} WHERE id = %s"
        cur.execute(query, values)
        
        if cur.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Note not found'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Note updated successfully'}), 200
    except Exception as e:
        logger.error(f"Error updating note: {e}")
        return jsonify({'error': 'Failed to update note'}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
        
        if cur.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Note not found'}), 404
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'message': 'Note deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        return jsonify({'error': 'Failed to delete note'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about notes"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM notes")
        total_notes = cur.fetchone()[0]
        
        cur.execute("SELECT category, COUNT(*) FROM notes GROUP BY category")
        categories = {}
        for row in cur.fetchall():
            categories[row[0]] = row[1]
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_notes': total_notes,
            'categories': categories
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        return jsonify({'error': 'Failed to retrieve stats'}), 500

# Initialize database when app starts
with app.app_context():
    init_db()

if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
