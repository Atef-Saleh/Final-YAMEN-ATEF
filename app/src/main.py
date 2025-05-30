import sys
import os
import json
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USERNAME', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'conversions')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kilometers = db.Column(db.Float, nullable=False)
    miles = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Conversion {self.kilometers}km to {self.miles}mi>'


with app.app_context():
    db.create_all()


def km_to_miles(kilometers):
    return kilometers * 0.621371


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.get_json()
    
    if not data or 'kilometers' not in data:
        return jsonify({'error': 'Invalid input. Please provide kilometers value.'}), 400
    
    try:
        kilometers = float(data['kilometers'])
    except ValueError:
        return jsonify({'error': 'Invalid input. Kilometers must be a number.'}), 400
    
    miles = km_to_miles(kilometers)
    
   
    try:
        new_conversion = Conversion(kilometers=kilometers, miles=miles)
        db.session.add(new_conversion)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Database error: {str(e)}")

    
    return jsonify({
        'kilometers': kilometers,
        'miles': round(miles, 2),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/history', methods=['GET'])
def history():

    conversions = Conversion.query.order_by(Conversion.timestamp.desc()).limit(10).all()
    
    history_list = [{
        'id': conv.id,
        'kilometers': conv.kilometers,
        'miles': round(conv.miles, 2),
        'timestamp': conv.timestamp.isoformat()
    } for conv in conversions]
    
    return jsonify(history_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('DEBUG', 'False').lower() == 'true')
