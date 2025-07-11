from flask import request
import psycopg2
import datetime
import pytz
import pycountry
import geocoder
from .db import get_connection

def regiset_routes(app):
    # people

    @app.route('/api/people', methods=['GET'])
    def get_all_people():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM people')
        data = cur.fetchall()
        result = []
        for i in data:
            if i[7]:
                continue
            else:
                result.append([i[0], i[1], i[2], i[3], i[4], i[5], i[6]])
        return {'data': result}

    @app.route('/api/people/<int:id_person>', methods=['GET'])
    def get_person(id_person):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT * FROM people WHERE "ID_person"=%s""", (id_person,))

        data = cur.fetchall()
        if data:
            if data[0][7]:
                return {'error': 'user deleted'}, 400
            result = [data[0][1], data[0][2], data[0][3], data[0][4], data[0][5], data[0][6]]
            return {'data': result}
        else:
            return {'error': 'person not found'}, 404

    @app.route('/api/people/', methods=['POST'])
    def post_person():
        conn = get_connection()
        cur = conn.cursor()

        errors = []

        data = request.get_json()

        first_name = data['first_name']
        surname = data['surname']
        pesel = data['pesel']
        document_nr = data['document_nr']
        document_type = data['document_type']
        birth_date = data['birth_date']

    # validations

    # first_name
        if first_name is None:
            errors.append({'field': 'first_name', 'message': 'first_name can not be empty'})

        if len(first_name) > 100:
            errors.append({'field': 'first_name', 'message': 'first_name can not be longer than 100 characters'})

    # surname
        if surname is None:
            errors.append({'field': 'surname', 'message': 'surname can not be empty'})

        if len(surname) > 100:
            errors.append({'field': 'surname', 'message': 'surname can not be longer than 100 characters'})

    # pesel and document validation
        if pesel is None:
            if document_nr is None:
                errors.append({'field': 'document_nr', 'message': 'document_nr and pesel can not be empty at the same time'})
            elif len(document_nr) > 20:
                errors.append({'field': 'document_nr', 'message': 'document_nr can not be longer than 20 characters'})
            if document_type is None:
                errors.append({'field': 'document_type', 'message': 'document_type and pesel can not be empty at the same time'})
            elif len(document_type) > 20:
                errors.append({'field': 'document_type', 'message': 'document_type can not be longer than 20 characters'})
        else:
            if len(pesel) == 11:
                cur.execute("""SELECT "pesel" FROM people""")
                data = cur.fetchall()
                pesels = [i[0] for i in data]
                if pesel in pesels:
                    errors.append({'field': 'pesel', 'message': 'pesel is already registered'})
                if len(document_nr) > 20:
                    errors.append({'field': 'document_nr', 'message': 'document_nr can not be longer than 20 characters'})
                if len(document_type) > 20:
                    errors.append({'field': 'document_type', 'message': 'document_type can not be longer than 20 characters'})
            else:
                errors.append({'fie.ld': 'pesel', 'message': 'pesel must be 11 characters long'})


    # date formating and eventual value error detection
        try:
            actual_birth_date = datetime.date.fromisoformat(birth_date)
        except ValueError:
            errors.append({'field': 'birth_date', 'message': 'wrong date format'})

        # error codes
        if errors.__len__() >= 1:
            return {'errors': errors}, 400

        cur.execute("""INSERT INTO people 
                    VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, DEFAULT);""",
                    (first_name, surname, pesel, document_nr, document_type, actual_birth_date,)
                    )
        new_id = "tmp"
        conn.commit()

        return {'message': f'person added succesfully', 'index': new_id}


    @app.route('/api/people/<int:id_person>', methods=['PUT'])
    def put_person(id_person):
        conn = get_connection()
        cur = conn.cursor()

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
        if new_first_name is None:
            errors.append({'field': 'first_name', 'message': 'first_name can not be empty'})

        if len(new_first_name) > 100:
            errors.append({'field': 'first_name', 'message': 'first_name can not be longer than 100 characters'})

    # surname
        if new_surname is None:
            errors.append({'field': 'surname', 'message': 'surname can not be empty'})

        if len(new_surname) > 100:
            errors.append({'field': 'surname', 'message': 'surname can not be longer than 100 characters'})

    # pesel and document validation
        if new_pesel is None:
            if new_document_nr is None:
                errors.append({'field': 'document_nr', 'message': 'document_nr and pesel can not be empty at the same time'})
            elif len(new_document_nr) > 20:
                errors.append({'field': 'document_nr', 'message': 'document_nr can not be longer than 20 characters'})
            if new_document_type is None:
                errors.append({'field': 'document_type', 'message': 'document_type and pesel can not be empty at the same time'})
            elif len(new_document_type) > 20:
                errors.append({'field': 'document_type', 'message': 'document_type can not be longer than 20 characters'})
        else:
            if len(new_pesel) == 11:
                pesels = [[x[0], x[3]] for x in data]
                for i in range(0, len(pesels)):
                    if pesels[i][1] == new_pesel:
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
        actual_birth_date = None
        try:
            actual_birth_date = datetime.date.fromisoformat(new_birth_date)
        except ValueError:
            errors.append({'field': 'birth_date', 'message': 'wrong date format'})

        # error codes
        if errors.__len__() >= 1:
            return {'errors': errors}, 422

        cur.execute("""UPDATE people SET "first_name" = %s, "surname" = %s, "pesel" = %s,
        "document_nr" = %s, "document_type" = %s, "birth_date" = %s  WHERE "ID_person" = %s""", (
            new_first_name, new_surname, new_pesel, new_document_nr, new_document_type, actual_birth_date, id_person,))
        conn.commit()
        return {'message': f'updated person with index {id_person}'}


    @app.route('/api/people/<int:id_person>', methods=['DELETE'])
    def delete_person(id_person):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT 'True' FROM reservations WHERE "ID_person" = %s AND "deleted" = FALSE;""", (id_person,))
        if cur.fetchall():
            return {'message': 'can not delete: there is reservation made by that person'}, 400
        else:
            cur.execute("""SELECT "deleted" from people WHERE "ID_person" = %s;""", (id_person,))
            data = cur.fetchall()
            if not data:
                return {'message': 'person not found'}, 404
            if data[0][0]:
                return {'message': 'person already deleted'}, 400

            cur.execute("""UPDATE people SET "first_name" = "deleted", "surname" = "deleted", "pesel" = NULL,
        "document_nr" = NULL, "document_type" = NULL, "birth_date" = %s, "deleted" = True  WHERE "ID_person" = %s""",
                        (datetime.datetime.today(), id_person,))
            conn.commit()
            return {'message': f'person deleted with index {id_person}'}

    # items


    @app.route('/api/items', methods=['GET'])
    def get_all_items():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM items')
        data = cur.fetchall()
        result = []
        for i in data:
            if i[5]:
                continue
            else:
                result.append([i[0], i[1], i[2], i[3], i[4]])
        return {'data': result}


    @app.route('/api/items/<int:id_item>', methods=['GET'])
    def get_item(id_item):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT * FROM items WHERE "ID_item"=%s AND "deleted" = false""", (id_item,))

        data = cur.fetchall()
        if data:
            if data[0][5]:
                return {'error': 'user deleted'}, 400
            result = [data[0][1], data[0][2], data[0][3], data[0][4]]
            return {'data': result}
        else:
            return {'error': 'item not found'}, 404


    @app.route('/api/items/', methods=['POST'])
    def post_item():
        conn = get_connection()
        cur = conn.cursor()

        errors = []

        data = request.get_json()

        name = data['name']
        description = data['description']
        item_type = data['type']
        adult_required = data['adult_required']

    # validations

    # name
        if name is None:
            errors.append({'field': 'name', 'message': 'name can not be empty'})

        if len(name) > 100:
            errors.append({'field': 'name', 'message': 'name can not be longer than 100 characters'})

        cur.execute("""SELECT "name" FROM items""")
        data = cur.fetchall()
        names = [i[0] for i in data]
        if name in names:
            errors.append({'field': 'name', 'message': 'name is already taken'})
    # description

        if len(description) > 2000:
            errors.append({'field': 'surname', 'message': 'surname can not be longer than 100 characters'})

    # type

        if len(item_type) > 20:
            errors.append({'field': 'type', 'message': 'type can not be longer than 20 characters'})

    # adult_required

        if adult_required is None:
            errors.append({'field': 'adult_required', 'message': 'adult_required can not be empty'})

        # error codes
        if errors.__len__() >= 1:
            return {'errors': errors}, 422

        cur.execute("""INSERT INTO items 
                    VALUES (DEFAULT, %s, %s, %s, %s, DEFAULT);""",
                    (name, description, item_type, adult_required,)
                    )
        new_id = "tmp"
        conn.commit()

        return {'message': f'item added', 'index': new_id}


    @app.route('/api/items/<int:id_item>', methods=['PUT'])
    def put_item(id_item):
        conn = get_connection()
        cur = conn.cursor()

        errors = []
        new_data = request.get_json()

        new_name = new_data['name']
        new_description = new_data['description']
        new_type = new_data['type']
        new_adult_required = new_data['adult_required']

        cur.execute("""SELECT "ID_item","name" FROM items""")
        data = cur.fetchall()

        ids = [x[0] for x in data]
        if id_item not in ids:
            return {'error': 'item not found'}, 404

    # validations

    # name
        if new_name is None:
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

        if new_adult_required is None:
            errors.append({'field': 'adult_required', 'message': 'adult_required can not be empty'})

        # error codes
        if errors.__len__() >= 1:
            return {'errors': errors}, 422

        cur.execute("""UPDATE items SET "name" = %s, "description" = %s, "type" = %s,
        "adult_required" = %s  WHERE "ID_item" = %s""", (
            new_name, new_description, new_type, new_adult_required, id_item,))
        conn.commit()
        return {'message': f'updated item with index {id_item}'}


    @app.route('/api/items/<int:id_item>', methods=['DELETE'])
    def delete_item(id_item):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT 'True' FROM reservations WHERE "ID_item" = %s AND "deleted" = FALSE;""", (id_item,))
        if cur.fetchall():
            return {'message': 'can not delete: there is reservation made on that item'}, 400
        else:
            cur.execute("""SELECT "deleted" from items WHERE "ID_item" = %s;""", (id_item,))
            data = cur.fetchall()
            if not data:
                return {'message': 'item not found'}, 404
            if data[0][0]:
                return {'message': 'item already deleted'}, 400

            cur.execute("""UPDATE items SET "name" = "deleted", "description" = NULL, "type" = "deleted",
            "adult_required" = False, "deleted" = True  WHERE "ID_item" = %s""",
                        (id_item,))
            conn.commit()
            return {'message': f'item deleted with index {id_item}'}


    # reservations


    @app.route('/api/reservations', methods=['GET'])
    def get_all_reservations():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute('SELECT * FROM reservations')
        data = cur.fetchall()
        result = []
        for i in data:
            if i[5]:
                continue
            else:
                result.append([i[0], i[1], i[2], i[3], i[4]])
        return {'data': result}


    @app.route('/api/reservations/<int:id_reserv>', methods=['GET'])
    def get_reservation(id_reserv):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT * FROM reservations WHERE "ID_reservation"=%s""", (id_reserv,))

        data = cur.fetchall()
        if data:
            if data[0][5]:
                return {'error': 'user deleted'}, 400
            result = [data[0][1], data[0][2], data[0][3], data[0][4]]
            return {'message': 'data taken succesfully', 'data': result}
        else:
            return {'error': 'item not found'}, 404


    @app.route('/api/reservations/', methods=['POST'])
    def post_reservation():
        conn = get_connection()
        cur = conn.cursor()

        errors = []

        data = request.get_json()
        id_person = data['ID_person']
        id_item = data['ID_item']
        starting_time = data['starting_time']
        ending_time = data['ending_time']

        correct_time = True

        if id_person is None:
            errors.append({'field': 'id_person', 'message': 'id_person can not be empty'})
        else:
            cur.execute("""SELECT "ID_person" FROM people WHERE "ID_person"=%s AND "deleted" = false""", (id_person,))
            people_check = cur.fetchall()
            if not people_check:
                errors.append({'field': 'ID_person', 'message': 'person not found'})

        if id_item is None:
            errors.append({'field': 'id_item', 'message': 'id_item can not be empty'})
        else:
            cur.execute("""SELECT "ID_item" FROM items WHERE "ID_item"=%s AND "deleted" = false""", (id_item,))
            items_check = cur.fetchall()
            if not items_check:
                errors.append({'field': 'ID_item', 'message': 'item not found'})

        if starting_time is None:
            correct_time = False
            errors.append({'field': 'starting_time', 'message': 'starting_time can not be empty'})
        else:
            try:
                parsed_start = datetime.datetime.fromisoformat(starting_time)
            except ValueError:
                correct_time = False
                errors.append({'field': 'starting_time', 'message': 'wrong date format'})

        if ending_time is None:
            correct_time = False
            errors.append({'field': 'ending_time', 'message': 'ending_time can not be empty'})
        else:
            try:
                parsed_end = datetime.datetime.fromisoformat(ending_time)
            except ValueError:
                correct_time = False
                errors.append({'field': 'ending_time', 'message': 'wrong date format'})

        g = geocoder.ip('me')
        country = pycountry.countries.get(alpha_2=g.country).name
        today = datetime.datetime.now(pytz.timezone(country))

        if correct_time:
            if parsed_start <= today:
                errors.append({'field': 'starting_time', 'message': 'starting_time must be in the future'})
            if parsed_end <= today:
                errors.append({'field': 'ending_time', 'message': 'ending_time must be in the future'})

            cur.execute("""SELECT "starting_time", "ending_time" FROM reservations WHERE ("starting_time" <= %s 
            AND "ending_time" >= %s) AND "ID_item" = %s AND "deleted" = false""", (parsed_start, parsed_end, id_item,))
            dates = cur.fetchall()

            if dates:
                errors.append({'field': 'starting_time ending_time', 'message': 'time period arleady taken'})

        if errors.__len__() >= 1:
            return {'errors': errors}, 400

        cur.execute("""INSERT INTO reservations 
                    VALUES (default, %s, %s, %s, %s, DEFAULT);""",
                    (id_person, id_item, parsed_start, parsed_end,))
        conn.commit()

        new_id = "tmp"
        return {'message': 'reservation added successfully', 'index': new_id}


    @app.route('/api/reservations/<int:id_reservation>', methods=['PUT'])
    def put_reservation(id_reservation):
        conn = get_connection()
        cur = conn.cursor()

        errors = []

        data = request.get_json()
        id_person = data['ID_person']
        id_item = data['ID_item']
        starting_time = data['starting_time']
        ending_time = data['ending_time']

        correct_time = True

        if id_person is None:
            errors.append({'field': 'id_person', 'message': 'id_person can not be empty'})
        else:
            cur.execute("""SELECT "ID_person" FROM people WHERE "ID_person"=%s AND "deleted" = false""", (id_person,))
            people_check = cur.fetchall()
            if not people_check:
                errors.append({'field': 'ID_person', 'message': 'person not found'})

        if id_item is None:
            errors.append({'field': 'id_item', 'message': 'id_item can not be empty'})
        else:
            cur.execute("""SELECT "ID_item" FROM items WHERE "ID_item"=%s AND "deleted" = false""", (id_item,))
            items_check = cur.fetchall()
            if not items_check:
                errors.append({'field': 'ID_item', 'message': 'item not found'})

        if starting_time is None:
            correct_time = False
            errors.append({'field': 'starting_time', 'message': 'starting_time can not be empty'})
        else:
            try:
                parsed_start = datetime.datetime.fromisoformat(starting_time)
            except ValueError:
                correct_time = False
                errors.append({'field': 'starting_time', 'message': 'wrong date format'})

        if ending_time is None:
            correct_time = False
            errors.append({'field': 'ending_time', 'message': 'ending_time can not be empty'})
        else:
            try:
                parsed_end = datetime.datetime.fromisoformat(ending_time)
            except ValueError:
                correct_time = False
                errors.append({'field': 'ending_time', 'message': 'wrong date format'})

        g = geocoder.ip('me')
        country = pycountry.countries.get(alpha_2=g.country).name
        today = datetime.datetime.now(pytz.timezone(country))

        if correct_time:
            if parsed_start <= today:
                errors.append({'field': 'starting_time', 'message': 'starting_time must be in the future'})
            if parsed_end <= today:
                errors.append({'field': 'ending_time', 'message': 'ending_time must be in the future'})

            cur.execute("""SELECT "starting_time", "ending_time" FROM reservations WHERE ("starting_time" <= %s 
            AND "ending_time" >= %s) AND "ID_item" = %s AND "deleted" = false""", (parsed_start, parsed_end, id_item,))
            dates = cur.fetchall()

            if dates:
                errors.append({'field': 'starting_time ending_time', 'message': 'time period arleady taken'})

        if errors.__len__() >= 1:
            return {'errors': errors}, 400

        cur.execute("""UPDATE reservations SET "ID_person" = %s, "ID_item" = %s, "starting_time" = %s, "ending_time" = %s 
                    WHERE "ID_reservation" = %s"""
                    , (id_person, id_item, parsed_start, parsed_end,id_reservation,))
        conn.commit()

        new_id = "tmp"
        return {'message': 'reservation altered successfully', 'index': new_id}

    @app.route('/api/reservations/<int:id_reservation>', methods=['DELETE'])
    def delete_reservation(id_reservation):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT "deleted" from reservations WHERE "ID_reservation" = %s;""", (id_reservation,))
        data = cur.fetchall()
        if not data:
            return {'message': 'reservation not found'}, 404
        if data[0][0]:
            return {'message': 'reservation already deleted'}, 400

        cur.execute("""UPDATE reservations SET "deleted" = TRUE WHERE "ID_reservation" = %s""", (id_reservation,))
        conn.commit()
        return {'message': f'reservation deleted with index {id_reservation}'}


    # searching

    @app.route('/api/search/user/<string:user>', methods=['GET'])
    def search_user(user):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT * FROM reservations res, people peo, items ite WHERE res."ID_person" = peo."ID_person" 
        AND res."ID_item" = ite."ID_item" AND (peo."first_name" LIKE {}
        OR peo."surname" LIKE {});""".format("'%" + user + "%'", "'%" + user + "%'"))

        data = cur.fetchall()

        if not data:
            return {'message': 'no reservations found'}, 404
        else:
            result = []
            for i in data:
                print(i)
                if not i[5]:
                    result.append([i[7], i[8], i[3], i[4], i[15], i[16], i[17]])

        if result:
            return {'reservations': result}, 200
        else:
            return {'message': 'no reservations found'}, 404


    @app.route('/api/search/item/<string:item>', methods=['GET'])
    def search_item(item):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""SELECT * FROM reservations res, people peo, items ite WHERE res."ID_person" = peo."ID_person" 
        AND res."ID_item" = ite."ID_item" AND (ite."name" LIKE {}
        OR ite."type" LIKE {});""".format("'%" + item + "%'", "'%" + item + "%'"))

        data = cur.fetchall()

        if not data:
            return {'message': 'no reservations found'}, 404
        else:
            result = []
            for i in data:
                if not i[5]:
                    return result.append([i[7], i[8], i[15], i[16], i[17], i[18], i[3], i[4]])
        print(result)
        if result:
            return {'reservations': result}, 200
        else:
            return {'message': 'no reservations found'}, 404
