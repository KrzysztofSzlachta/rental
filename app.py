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

# people


@app.route('/api/people', methods=['GET'])
def get_all_people():
    cur.execute('SELECT * FROM people')
    return {'message': 'data taken succesfully', 'data': cur.fetchall()}


@app.route('/api/people/<int:id_person>', methods=['GET'])
def get_person(id_person):
    cur.execute("""SELECT * FROM people WHERE "ID_person"=%s""", (id_person,))

    result = cur.fetchall()
    if result:
        return {'message': 'data taken succesfully', 'data': result}
    else:
        return {'error': 'person not found'}, 404


@app.route('/api/people/', methods=['POST'])
def post_person():
    errors = []

    data = request.get_json()

    first_name = data['first_name']
    surname = data['surname']
    pesel = data['pesel']
    document_nr = data['document_nr']
    document_type = data['document_type']
    birth_date = data['birth_date']

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

    return {'message': f'person added with index {id_person}'}


@app.route('/api/people/<int:id_person>', methods=['PUT'])
def put_person(id_person):
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

    ids = [x[0] for x in data]
    if id_person not in ids:
        return {'error': 'person not found'}, 404

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
            pesels = [[x[0], x[3]] for x in data]
            for i in range(0, len(pesels)):
                if pesels[i][1] == int(new_pesel):
                    if pesels[i][0] == id_person:
                        break
                    else:
                        errors.append({'field': 'pesel', 'message': 'pesel is already registered'})
                        break
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

    cur.execute("""UPDATE people SET "first_name" = %s, "surname" = %s, "pesel" = %s,
    "document_nr" = %s, "document_type" = %s, "birth_date" = %s  WHERE "ID_person" = %s""", (
        new_first_name, new_surname, new_pesel, new_document_nr, new_document_type, new_birth_date, id_person,))
    return {'message': f'updated person with index {id_person}'}


@app.route('/api/people/<int:id_person>', methods=['DELETE'])
def delete_person(id_person):
    cur.execute("""DELETE FROM people WHERE "ID_person" = %s;""",(id_person,))
    return {'message': f'person deleted with index {id_person}'}

# items


@app.route('/api/items', methods=['GET'])
def get_all_items():
    cur.execute('SELECT * FROM items')
    return {'message': 'data taken succesfully', 'data': cur.fetchall()}


@app.route('/api/items/<int:id_item>', methods=['GET'])
def get_item(id_item):
    cur.execute("""SELECT * FROM items WHERE "ID_item"=%s""", (id_item,))

    result = cur.fetchall()
    if result:
        return {'message': 'data taken succesfully', 'data': result}
    else:
        return {'error': 'item not found'}, 404

@app.route('/api/items/', methods=['POST'])
def post_item():
    errors = []

    data = request.get_json()

    name = data['name']
    description = data['description']
    item_type = data['type']
    adult_required = data['adult_required']

# ID creation (it could be replaced by making the column in database a serial data type)

    cur.execute("""SELECT * FROM items;""")
    data = cur.fetchall()
    ids = [x[0] for x in data]
    id_item = 0
    for i in range(1, len(ids) + 2):
        if i not in ids:
            id_item = i

# validations

# name
    if name == 'Null':
        errors.append({'field': 'name', 'message': 'name can not be empty'})

    if len(name) > 100:
        errors.append({'field': 'name', 'message': 'name can not be longer than 100 characters'})

    names = [x[1] for x in data]
    if name in names:
        errors.append({'field': 'name', 'message': 'name is already taken'})
# description

    if len(description) > 2000:
        errors.append({'field': 'surname', 'message': 'surname can not be longer than 100 characters'})

# type

    if len(item_type) > 20:
        errors.append({'field': 'type', 'message': 'type can not be longer than 20 characters'})

# adult_required

    if adult_required == "Null":
        errors.append({'field': 'adult_required', 'message': 'adult_required can not be empty'})

    # error codes
    if errors.__len__() >= 1:
        return {'errors': errors}, 422

    cur.execute("""INSERT INTO items 
                VALUES (%s, %s, %s, %s, %s);""",
                (id_item, name, description, item_type, adult_required,)
                )

    return {'message': f'item added with index {id_item}'}


@app.route('/api/items/<int:id_item>', methods=['PUT'])
def put_item(id_item):
    errors = []
    new_data = request.get_json()

    new_name = new_data['name']
    new_description = new_data['description']
    new_type = new_data['type']
    new_adult_required = new_data['adult_required']

    cur.execute("""SELECT * FROM items""")
    data = cur.fetchall()

    ids = [x[0] for x in data]
    if id_item not in ids:
        return {'error': 'item not found'}, 404

# validations

# name
    if new_name == 'Null':
        errors.append({'field': 'name', 'message': 'name can not be empty'})

    if len(new_name) > 100:
        errors.append({'field': 'name', 'message': 'name can not be longer than 100 characters'})

    names = [[x[0], x[1]] for x in data]
    for i in range(0, len(names)):
        if names[i][1] == new_name:
            if names[i][0] == id_item:
                break
            else:
                errors.append({'field': 'name', 'message': 'name is already taken'})
                break
# description

    if len(new_description) > 2000:
        errors.append({'field': 'surname', 'message': 'surname can not be longer than 100 characters'})

# type

    if len(new_type) > 20:
        errors.append({'field': 'type', 'message': 'type can not be longer than 20 characters'})

# adult_required

    if new_adult_required == "Null":
        errors.append({'field': 'adult_required', 'message': 'adult_required can not be empty'})

    # error codes
    if errors.__len__() >= 1:
        return {'errors': errors}, 422

    cur.execute("""UPDATE items SET "name" = %s, "description" = %s, "type" = %s,
    "adult_required" = %s  WHERE "ID_item" = %s""", (
        new_name, new_description, new_type, new_adult_required, id_item,))
    return {'message': f'updated item with index {id_item}'}


@app.route('/api/items/<int:id_item>', methods=['DELETE'])
def delete_item(id_item):
    cur.execute("""DELETE FROM items WHERE "ID_item" = %s;""", (id_item,))
    return {'message': f'item deleted with index {id_item}'}


# reservations


@app.route('/api/reservations', methods=['GET'])
def get_all_reservations():
    cur.execute('SELECT * FROM reservations')
    return {'message': 'data taken succesfully', 'data': cur.fetchall()}


@app.route('/api/reservations/<int:id_reserv>', methods=['GET'])
def get_reservation(id_reserv):
    cur.execute("""SELECT * FROM reservations WHERE "ID_reservation"=%s""", (id_reserv,))

    result = cur.fetchall()
    if result:
        return {'message': 'data taken succesfully', 'data': result}
    else:
        return {'error': 'item not found'}, 404

if __name__ == '__main__':
    app.run(debug=True)
