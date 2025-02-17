def test_index(client):
    response = client.get('/auth') 
    reponse_json = response.get_json() 
    users = reponse_json['users']
    
    assert response.status_code == 200 
    if users:
        assert type(users[0]) == dict
   

def test_register(client):
    register_data = {
        "first_name": "teacher9",
        "last_name": "teacher9",
        "email" : "teacher9@gmail.com",
        "username" :"teacher9",
        "password": "Test@123",
        "role" : 2
    }

    response = client.post('/auth/register', json=register_data)  
    
    assert response.status_code == 201
    assert response.json == {"message": "Registration successful"}

def test_login_success(client):
    login_data = {
        'username': "teacher",
        'password': "Test@123"
    }

    response = client.post('/auth/login', json=login_data)
    response_json = response.get_json()
    
    assert response.status_code == 200
    assert 'access_token' in response_json 

def test_auth_user(client, auth):
    headers = auth.login('teacher','Test@123')
    response = client.get('/auth/auth-user', headers=headers)
    json_data = response.get_json()

    assert response.status_code == 200  
    assert "user" in json_data  

def test_logout(client, auth):
    headers = auth.login('teacher','Test@123')
    response = client.post('/auth/logout', headers=headers)

    assert response.status_code == 200
    assert response.json == {'message': 'Successfully logged out'}  