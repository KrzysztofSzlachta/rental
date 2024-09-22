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

@app.route('/api/subject?name=<wanted_name>&sortField=<sort_field>&sortOrder=<sort_order>&pageSize=<int: page_size>&pageNumber=<int: page_number>&code=<searched_code>')
def get_search(wanted_name, sort_field, sort_order, page_size, page_number, searched_code):
    designates_subjects = []
    for i in range((page_number-1) * page_size, (page_number-1) * page_size + page_size):
        if wanted_name == subjects[i]['name'] and searched_code == subjects[i]['code']:
            designates_subjects.append(subjects[i])
    designates_subjects = sorted(designates_subjects, key=lambda k: k['name'])
    return designates_subjects

if __name__ == '__main__':
    app.run(debug=True)
