def get_header(auth):
    return auth.login('teacher', 'Test@123')

def test_teacher_dashboard(client, auth):
    headers = get_header(auth) 

    response = client.get('/teacher/dashboard', headers=headers)
    response_json = response.get_json()

    assert response.status_code == 200
    assert 'student_mark_list' in response_json 

def test_get_students(client, auth):
    headers = get_header(auth) 

    response = client.get('/teacher/students', headers=headers)

    assert response.status_code == 200
    assert 'student_list' in response.get_json()

def test_teacher_profile(client, auth):
    headers = get_header(auth)

    data = {
        "first_name": "teacher",
        "last_name": "teacher",
        "email": "teacher@gmail.com",
        "username": "teacher",
        "phone_number": "9876565871",
        "address" : "Mumbai",
        "education" : "BSC",
        "gender" : "M",
        "subject" : 1,
    }  

    response = client.put('/teacher/profile', headers=headers, json=data)

    assert response.status_code == 200
    assert response.json ==  {'message': 'User updated successfully'} 