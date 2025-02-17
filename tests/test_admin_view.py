def get_header(auth):
    return auth.login('admin', 'Test@123')

def test_admin_dashboard(client, auth):
    headers = get_header(auth)

    response = client.get('/admin/dashboard', headers=headers)

    assert response.status_code == 200
    response_json = response.get_json()
    expected_keys = {"active_student", "active_teacher", "inactive_student", "inactive_teacher"}

    assert expected_keys.issubset(response_json["data"].keys())

def test_admin_profile(client, auth):
    headers = get_header(auth)

    data = {
        "first_name": "admin",
        "last_name": "admin",
        "email": "admin@gmail.com",
        "username": "admin",
        "phone_number": "9876562890"
    }

    response = client.put('/admin/profile', headers=headers, json=data)

    assert response.status_code == 200
    assert response.json == {'message': 'User updated'}

def test_get_classes(client,auth):
    headers = get_header(auth)

    response = client.get('/admin/classes', headers=headers) 

    assert response.status_code == 200
    response_data = response.get_json()   

    assert "classes" in response_data

def test_create_subject(client,auth):
    headers = get_header(auth)

    data = {
        "name": "History"
    }   

    response = client.post('/admin/create-subject', headers=headers, json=data)

    assert response.status_code == 200
    assert response.json == {'message' : 'Subject created successfully'}

def test_update_subject(client, auth):
    headers = get_header(auth) 

    data = { "name" : "English"}

    response = client.put('/admin/update-subject/1', headers=headers, json=data)

    assert response.status_code == 200
    assert response.json == {'message' : 'Subject edit successfully'}

def test_update_subject_fail(client, auth):
    headers = get_header(auth) 

    data = { "name" : "Hindi"}

    response = client.put('/admin/update-subject/1', headers=headers, json=data)

    assert response.status_code == 403
    assert response.json == {'error': 'Already exist'}   

# def test_delete_subject(client, auth):
#     headers = get_header(auth)

#     response = client.delete('/admin/delete-subject/1', headers=headers) 

#     assert response.status_code ==200
#     assert response.json == {'message': 'Subject and its references removed successfully from teacher profiles and classes'}    

def test_get_students(client, auth):
    headers = get_header(auth)

    response = client.get('/admin/students', headers=headers)
    response_json = response.get_json()
    students = response_json['students']

    assert response.status_code == 200

    if students:
        assert students[0]['role'] == 3

def test_change_user_status(client, auth):
    headers = get_header(auth)

    response = client.get('/admin/change-status/2', headers=headers)   

    assert response.status_code == 200
    assert response.json == {'message': 'Status hasn been changed'} 

def test_delete_user(client, auth):
    headers = get_header(auth)

    response = client.delete('/admin/delete-user/2', headers=headers)

    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}  

def test_get_user(client, auth):
    headers = get_header(auth)

    response = client.get('/admin/get-user/2',headers=headers)
    response_data = response.get_json()
    user = response_data['user']

    assert response.status_code == 200 

    if user:
        assert user['id'] == 2

def test_get_teachers(client, auth):
    headers = get_header(auth)

    response = client.get('/admin/teachers', headers=headers)
    response_data = response.get_json()
    teachers = response_data['teachers']   

    assert response.status_code == 200

    if teachers:
        assert teachers[0]['role'] == 2  

def test_assign_class_teacher(client, auth):
    headers = get_header(auth)

    response = client.get('/admin/assign-class-teacher/2/2', headers=headers)

    assert response.status_code == 200
    assert response.json == {'message' : 'Class added successfully'}   

def test_add_class_subject_fail(client, auth):
    headers = get_header(auth)

    data = {
        'class_subject' : [1,2,7,8]
    }  

    response = client.post('/admin/add-class-subject/1', headers=headers, json=data) 
    assert response.status_code == 422
    assert response.json == {'message': 'class_subject value is not correct'} 

def test_add_class_subject_success(client, auth):
    headers = get_header(auth) 

    data = {
        'class_subject' : [1,2]
    }  

    reponse = client.post('/admin/add-class-subject/1', headers=headers, json=data) 

    assert reponse.status_code == 200
    assert reponse.json == {'message': "Subject list added to class successfully"}

def test_get_subjects(client, auth):
    headers = get_header(auth) 

    response = client.get('/admin/subjects', headers=headers) 
    reponse_json = response.get_json() 
    subjects = reponse_json['subjects']
    
    assert response.status_code == 200 
    if subjects:
        assert type(subjects[0]) == dict  