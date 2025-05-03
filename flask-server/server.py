from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:aifg5656@localhost/fitness_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# FitnessClass Model (Table)
class FitnessClass(db.Model):
    __tablename__ = 'Classes'
    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('Trainers.trainer_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('Rooms.id'), nullable=False)
    restrictions = db.Column(db.String(255), nullable=True)
    
class Trainer(db.Model):
    __tablename__ = 'Trainers'
    trainer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.Integer, nullable=True)

class Room(db.Model):
    __tablename__ = 'Rooms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    building = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(50), nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    equipment = db.Column(db.String(255), nullable=True)

class Member(db.Model):
    __tablename__ = 'Members'
    mem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_vip = db.Column(db.Boolean, default=False)

class ClassParticipant(db.Model):
    __tablename__ = 'ClassParticipants'
    class_id = db.Column(db.Integer, db.ForeignKey('Classes.class_id'), primary_key=True)
    mem_id = db.Column(db.Integer, db.ForeignKey('Members.mem_id'), primary_key=True)

# Classes operations
@app.route('/api/classes', methods=['POST'])
def add_class():
    data = request.get_json()

    new_class = FitnessClass(
        description=data['description'],
        date=data['date'],
        time=data['time'],
        duration=data['duration'],
        trainer_id=data['trainer_id'],
        room_id=data['room_id'],
        restrictions=data.get('restrictions', None)  # Optional
    )
    try:
        db.session.add(new_class)
        db.session.commit()
        return jsonify({'message': 'Class added successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route("/api/classes/<int:class_id>", methods=["DELETE"])
def delete_class(class_id):
    try:
        ClassParticipant.query.filter_by(class_id=class_id).delete()

        class_to_delete = FitnessClass.query.get(class_id)
        if class_to_delete:
            db.session.delete(class_to_delete)

        db.session.commit()
        return jsonify({"success": True, "message": "Class and associated participants deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/classes/<int:class_id>", methods=["PUT"])
def update_class(class_id):
    try:
        data = request.json
        FitnessClass.query.filter_by(class_id=class_id).update({
            "description": data.get("description"),
            "date": data.get("date"),
            "time": data.get("time"),
            "duration": data.get("duration"),
            "trainer_id": data.get("trainer_id"),
            "room_id": data.get("room_id"),
            "restrictions": data.get("restrictions"),
        })
        db.session.commit()
        return jsonify({"success": True, "message": "Class updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
    
@app.route("/api/classes", methods=["GET"])
def fetch_classes():
    date_from = request.args.get("dateFrom")
    date_to = request.args.get("dateTo")
    trainer_id = request.args.get("trainer")
    room_id = request.args.get("room")

    # Convert empty strings to None (NULL in SQL)
    date_from = date_from if date_from else None
    date_to = date_to if date_to else None
    trainer_id = trainer_id if trainer_id else None
    room_id = room_id if room_id else None

    sql = text("""
        SELECT class_id, description, date, time, duration, trainer_id, room_id, restrictions
        FROM Classes
        WHERE (:date_from IS NULL OR date >= :date_from)
        AND (:date_to IS NULL OR date <= :date_to)
        AND (:trainer_id IS NULL OR trainer_id = :trainer_id)
        AND (:room_id IS NULL OR room_id = :room_id)
    """)

    result = db.session.execute(sql, {
        "date_from": date_from,
        "date_to": date_to,
        "trainer_id": trainer_id,
        "room_id": room_id
    }).fetchall()

    classes = []
    for row in result:
        duration_str = str(row.duration) if row.duration is not None else "00:00:00"
        classes.append({
            "class_id": row.class_id,
            "description": row.description,
            "date": str(row.date),
            "time": str(row.time),
            "duration": duration_str,
            "trainer_id": row.trainer_id,
            "room_id": row.room_id,
            "restrictions": row.restrictions
        })

    return jsonify({"classes": classes})

@app.route("/api/stats", methods=["GET"])
def fetch_class_statistics():
    date_from = request.args.get("dateFrom")
    date_to = request.args.get("dateTo")
    trainer_id = request.args.get("trainer")
    room_id = request.args.get("room")
    date_from = date_from if date_from else None
    date_to = date_to if date_to else None
    trainer_id = trainer_id if trainer_id else None
    room_id = room_id if room_id else None

    sql = text("""
        SELECT 
            AVG(duration) AS avg_duration,
            AVG(participant_count) AS avg_participants,
            AVG(vip_count) AS avg_vips
        FROM (
            SELECT 
                Cl.class_id,
                Cl.duration,
                COUNT(CP.mem_id) AS participant_count,
                SUM(CASE WHEN M.is_vip = 1 THEN 1 ELSE 0 END) AS vip_count
            FROM Classes Cl
            LEFT JOIN ClassParticipants CP ON Cl.class_id = CP.class_id
            LEFT JOIN Members M ON CP.mem_id = M.mem_id
            WHERE (:date_from IS NULL OR Cl.date >= :date_from)
            AND (:date_to IS NULL OR Cl.date <= :date_to)
            AND (:trainer_id IS NULL OR Cl.trainer_id = :trainer_id)
            AND (:room_id IS NULL OR Cl.room_id = :room_id)
            GROUP BY Cl.class_id
        ) AS class_stats;
    """)

    result = db.session.execute(sql, {
        "date_from": date_from,
        "date_to": date_to,
        "trainer_id": trainer_id,
        "room_id": room_id
    }).fetchone()

    return jsonify({
        "average_duration": float(result.avg_duration) if result.avg_duration is not None else 0,
        "average_participants": float(result.avg_participants) if result.avg_participants is not None else 0,
        "average_vips": float(result.avg_vips) if result.avg_vips is not None else 0
    })



# Trainers operations
@app.route('/api/trainers', methods=['GET'])
def get_trainers():
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT trainer_id, name FROM Trainers")
        trainers = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        return jsonify(trainers)
    finally:
        cursor.close()
        connection.close()

# Rooms operations
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    connection = db.engine.raw_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, CONCAT(building, ' - ', number) FROM Rooms")
        rooms = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        return jsonify(rooms)
    finally:
        cursor.close()
        connection.close()

# Search bar functionality
@app.route('/api/search-members')
def search_members():
    name_query = request.args.get('name', '').strip()
    class_id = request.args.get('class', type=int)
    if not name_query or class_id is None:
        return jsonify([])

    matching_members = Member.query.filter(Member.name.like(f"{name_query.capitalize()}%")).all()
    registered_ids = set(
        row.mem_id for row in
        db.session.query(ClassParticipant.mem_id)
        .filter_by(class_id=class_id)
        .all()
    )

    return jsonify([
        {
            "mem_id": m.mem_id,
            "name": m.name,
            "email": m.email,
            "registered": m.mem_id in registered_ids
        }
        for m in matching_members
    ])

# Restering member
@app.route('/api/register', methods=['POST'])
def register_member():
    data = request.get_json()
    class_id = data.get('class_id')
    mem_id = data.get('mem_id')
    if not class_id or not mem_id:
        return jsonify({"error": "Missing class_id or mem_id"}), 400
    # Extra check accounting for cuncurrency
    existing = ClassParticipant.query.filter_by(class_id=class_id, mem_id=mem_id).first()
    if existing:
        return jsonify({"error": "already registered"}), 500
    
    new_entry = ClassParticipant(class_id=class_id, mem_id=mem_id)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"status": "registered"})

# Deregistering member
@app.route('/api/deregister', methods=['POST'])
def deregister_member():
    data = request.get_json()
    class_id = data.get('class_id')
    mem_id = data.get('mem_id')
    if not class_id or not mem_id:
        return jsonify({"error": "Missing class_id or mem_id"}), 400
    # Perform extra checking to account for concurrency
    participant = ClassParticipant.query.filter_by(class_id=class_id, mem_id=mem_id).first()
    if not participant:
        return jsonify({"error": "not registered"}), 500

    db.session.delete(participant)
    db.session.commit()
    return jsonify({"status": "deregistered"})

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # app.run(port=5000)
    app.run(host='0.0.0.0', port=os.getenv('PORT', 5000))
