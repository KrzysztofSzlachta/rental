from flask import Flask, request

app = Flask(__name__)

subjects = [{'subject_id': 1, 'name': 'test', 'code': '2137'}]


@app.route('/api/subject', methods=['GET'])
def get_subjects():
    return subjects


@app.route('/api/subject/<int:subject_id>', methods=['GET'])
def get_subject(subject_id):
    chosen_subject = None
    for subject in subjects:
        if subject['subject_id'] == subject_id:
            chosen_subject = subject

    if chosen_subject is None:
        return {'message': 'Nie znaleziono obiektu o takim id.'}, 404

    return chosen_subject


@app.route('/api/subject', methods=['POST'])
def post_subjects():
    max_id = 1
    for subject in subjects:
        if subject['subject_id'] > max_id:
            max_id = subject['subject_id']
    request_data = request.get_json()
    new_subject = {'subject_id': max_id + 1, 'name': request_data['name'], 'code': request_data['code']}
    subjects.append(new_subject)
    return {'message': 'Obiekt pomyślnie dodany', 'subject_id': new_subject['subject_id']}, 201


@app.route('/api/subject/<int:subject_id>', methods=['PUT'])
def put_subjects(subject_id):
    chosen_subject = None
    for subject in subjects:
        if subject['subject_id'] == subject_id:
            chosen_subject = subject

    if chosen_subject is None:
        return {'message': 'Nie znaleziono obiektu o takim id.'}, 404

    new_data = request.get_json()

    chosen_subject['name'] = new_data['name']
    chosen_subject['code'] = new_data['code']

    return {'message': 'Dane zostały pomyślnie przypisane'}


@app.route('/api/subject/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    for i in range(0, len(subjects)):
        if subjects[i]['subject_id'] == subject_id:
            subjects.pop(i)
            return {'message': 'Obiekt pomyślnie usunięty.'}

    return {'message': 'Nie znaleziono obiektu o takim id.'}, 404


if __name__ == '__main__':
    app.run(debug=True)
