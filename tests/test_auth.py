def test_login_success(client):
    res = client.post('/api/auth/login', json={
        'email': 'doctor@mediscan.org',
        'password': 'Doctor123!'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['user']['role_name'] == 'DOCTOR'

def test_login_invalid_password(client):
    res = client.post('/api/auth/login', json={
        'email': 'doctor@mediscan.org',
        'password': 'WrongPassword!'
    })
    assert res.status_code == 401

def test_logout(client):
    client.post('/api/auth/login', json={'email': 'doctor@mediscan.org', 'password': 'Doctor123!'})
    res = client.post('/api/auth/logout')
    assert res.status_code == 200
