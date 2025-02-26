from flask import Flask, request
import psycopg2
import datetime

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="1234"
)

cur = conn.cursor()
app = Flask(__name__)


@app.route('/api/osoby', methods=['GET'])
def get_all_users():
    cur.execute('SELECT * FROM osoby')
    return cur.fetchall()


# @app.route('/api/osoby/<int:user_id>', methods=['GET'])
# def get_user(user_id):
#     cur.execute('SELECT * FROM osoby WHERE ID_osoby=%s', (user_id,))
#
#     result = cur.fetchall()
#     if result:
#         return cur.fetchall()
#     else:
#         return {'error': 'User not found'}, 404

@app.route('/api/osoby', methods=['POST'])
def post_subjects():
    cur.execute("""INSERT INTO osoby 
                VALUES (%s);""",
                (1,)
                )


# @app.route('/api/subject/<int:subject_id>', methods=['PUT'])
# def put_subjects(subject_id):
#     chosen_subject = None
#     for subject in subjects:
#         if subject['subject_id'] == subject_id:
#             chosen_subject = subject
#
#     if chosen_subject is None:
#         return {'message': 'Nie znaleziono obiektu o takim id.'}, 404
#
#     new_data = request.get_json()
#
#     chosen_subject['name'] = new_data['name']
#     chosen_subject['code'] = new_data['code']
#
#     return {'message': 'Dane zostały pomyślnie przypisane'}
#
#
# @app.route('/api/subject/<int:subject_id>', methods=['DELETE'])
# def delete_subject(subject_id):
#     for i in range(0, len(subjects)):
#         if subjects[i]['subject_id'] == subject_id:
#             subjects.pop(i)
#             return {'message': 'Obiekt pomyślnie usunięty.'}
#
#     return {'message': 'Nie znaleziono obiektu o takim id.'}, 404


if __name__ == '__main__':
    app.run(debug=True)
