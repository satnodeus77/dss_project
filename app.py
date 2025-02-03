from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Criteria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False, default=1.0)
    is_active = db.Column(db.Boolean, default=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(50))
    parameters = db.Column(db.Text)
    result = db.Column(db.Text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/criteria', methods=['GET', 'POST'])
def manage_criteria():
    if request.method == 'GET':
        criteria = Criteria.query.all()
        return jsonify([{'id': crit.id, 'name': crit.name, 'weight': crit.weight, 'is_active': crit.is_active} for crit in criteria])

    data = request.json
    if data['action'] == 'add':
        new_criteria = Criteria(name=data['name'], weight=data['weight'])
        db.session.add(new_criteria)
        db.session.commit()
    elif data['action'] == 'delete':
        Criteria.query.filter_by(id=data['id']).delete()
        db.session.commit()
    elif data['action'] == 'toggle':
        crit = Criteria.query.get(data['id'])
        crit.is_active = not crit.is_active
        db.session.commit()
    
    return jsonify({'message': 'Success'})

@app.route('/calculate', methods=['POST'])
def calculate():
    method = request.json.get('method')
    criteria = Criteria.query.filter_by(is_active=True).all()
    
    results = [{'name': crit.name, 'score': crit.weight} for crit in criteria]
    results = sorted(results, key=lambda x: x['score'], reverse=True)

    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
