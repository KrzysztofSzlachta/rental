from flask import Flask, request
import psycopg2
import datetime

conn = psycopg2.connect(
    dbname="rentals",
    user="postgres",
    password="1234"
)

cur = conn.cursor()
app = Flask(__name__)


@app.route('/api/people', methods=['GET'])
def get_all_users():
    cur.execute('SELECT * FROM people')
    return {'message': 'Data taken succesfully', 'data': cur.fetchall()}


# @app.route('/api/osoby/<int:user_id>', methods=['GET'])
# def get_user(user_id):
#     cur.execute('SELECT * FROM osoby WHERE ID_osoby=%s', (user_id,))
#
#     result = cur.fetchall()
#     if result:
#         return cur.fetchall()
#     else:
#         return {'error': 'User not found'}, 404

@app.route('/api/people/<string:first_name>&<string:surname>&<string:pesel>&<string:document_nr>&'
           '<string:document_type>&<string:birth_date>', methods=['POST'])
def post_subjects(first_name, surname, pesel, document_nr, document_type, birth_date):
    errors = []

# ID creation (it could be replaced by making the column in database a serial data type)

    cur.execute("""SELECT * FROM people;""")
    data = cur.fetchall()
    IDs = [x[0] for x in data]
    id_person = 0
    for i in range(1, len(IDs) + 2):
        if i not in IDs:
            id_person = i

# validations

# first_name
    if first_name == 'Null':
        errors.append({'field': 'first_name', 'message': 'first_name can not be empty'})

    if len(first_name) > 100:
        errors.append({'field': 'first_name', 'message': 'first_name can not be longer than 100 characters'})

# surname
    if surname == 'Null':
        errors.append({'field': 'surname', 'message': 'surname can not be empty'})

    if len(surname) > 100:
        errors.append({'field': 'surname', 'message': 'surname can not be longer than 100 characters'})

# pesel and document validation
    if pesel == 'Null':
        pesel = None
        if document_nr == 'Null':
            errors.append({'field': 'document_nr', 'message': 'document_nr and pesel can not be empty at the same time'})
        elif len(document_nr) > 20:
            errors.append({'field': 'document_nr', 'message': 'document_nr can not be longer than 20 characters'})
        if document_type == 'Null':
            errors.append({'field': 'document_type', 'message': 'document_type and pesel can not be empty at the same time'})
        elif len(document_type) > 20:
            errors.append({'field': 'document_type', 'message': 'document_type can not be longer than 20 characters'})
    else:
        if len(pesel) == 11:
            pesels = [x[3] for x in data]
            if int(pesel) in pesels:
                errors.append({'field': 'pesel', 'message': 'pesel is already registered'})
            if len(document_nr) > 20:
                errors.append({'field': 'document_nr', 'message': 'document_nr can not be longer than 20 characters'})
            if len(document_type) > 20:
                errors.append({'field': 'document_type', 'message': 'document_type can not be longer than 20 characters'})
        else:
            errors.append({'field': 'pesel', 'message': 'pesel must be 11 characters long'})


# date formating and eventual value error detection
    try:
        actual_birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
    except ValueError:
        errors.append({'field': 'birth_date', 'message': 'wrong date format'})

    # error codes
    if errors.__len__() >= 1:
        return {'errors': errors}, 422

    cur.execute("""INSERT INTO people 
                VALUES (%s, %s, %s, %s, %s, %s, %s);""",
                (id_person, first_name, surname, pesel, document_nr, document_type, actual_birth_date,)
                )

    return {'message': f'Person added with index {id_person}'}


@app.route('/api/people/<int:id_person>', methods=['PUT'])
def put_subjects(id_person):
    errors = []
    new_data = request.get_json()

    new_first_name = new_data['first_name']
    new_surname = new_data['surname']
    new_pesel = new_data['pesel']
    new_document_nr = new_data['document_nr']
    new_document_type = new_data['document_type']
    new_birth_date = new_data['birth_date']

    cur.execute("""SELECT * FROM people""")
    data = cur.fetchall()
# first_name
    if new_first_name == 'Null':
        errors.append({'field': 'first_name', 'message': 'first_name can not be empty'})

    if len(new_first_name) > 100:
        errors.append({'field': 'first_name', 'message': 'first_name can not be longer than 100 characters'})

# surname
    if new_surname == 'Null':
        errors.append({'field': 'surname', 'message': 'surname can not be empty'})

    if len(new_surname) > 100:
        errors.append({'field': 'surname', 'message': 'surname can not be longer than 100 characters'})

# pesel and document validation
    if new_pesel == 'Null':
        new_pesel = None
        if new_document_nr == 'Null':
            errors.append({'field': 'document_nr', 'message': 'document_nr and pesel can not be empty at the same time'})
        elif len(new_document_nr) > 20:
            errors.append({'field': 'document_nr', 'message': 'document_nr can not be longer than 20 characters'})
        if new_document_type == 'Null':
            errors.append({'field': 'document_type', 'message': 'document_type and pesel can not be empty at the same time'})
        elif len(new_document_type) > 20:
            errors.append({'field': 'document_type', 'message': 'document_type can not be longer than 20 characters'})
    else:
        if len(new_pesel) == 11:
            pesels = [x[3] for x in data]
            if int(new_pesel) in pesels:
                errors.append({'field': 'pesel', 'message': 'pesel is already registered'})
            if len(new_document_nr) > 20:
                errors.append({'field': 'document_nr', 'message': 'document_nr can not be longer than 20 characters'})
            if len(new_document_type) > 20:
                errors.append({'field': 'document_type', 'message': 'document_type can not be longer than 20 characters'})
        else:
            errors.append({'field': 'pesel', 'message': 'pesel must be 11 characters long'})

# date formating and eventual value error detection
    try:
        actual_birth_date = datetime.datetime.strptime(new_birth_date, '%Y-%m-%d').date()
    except ValueError:
        errors.append({'field': 'birth_date', 'message': 'wrong date format'})

    # error codes
    if errors.__len__() >= 1:
        return {'errors': errors}, 422

    cur.execute("""UPDATE people SET (first_name = new_first_name, surname = new_surname, pesel = new_pesel,
    document_nr = new_document_nr, document_type = new_document_type, birth_date = new_birth_date,) """)
    return {'message': f'updated person with index {id_person}'}

@app.route('/api/people/<int:id_person>', methods=['DELETE'])
def delete_subject(id_person):
    cur.execute("""DELETE FROM people WHERE (ID_person=%s);""",(id_person))
    return {'message': f'person deleted with index {id_person}'}

if __name__ == '__main__':
    app.run(debug=True)
