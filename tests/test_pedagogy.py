from app.services.pedagogy_seed import ensure_pedagogical_seed


def register_user(client, name, email, password):
    return client.post('/users', json={'name': name, 'email': email, 'password': password})


def login_user(client, email, password):
    return client.post('/auth/login', data={'username': email, 'password': password})


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


def test_placement_engine_and_dashboard(client, db_session):
    ensure_pedagogical_seed(db_session)

    res = register_user(client, 'Ped', 'ped@example.com', 'secret123')
    assert res.status_code == 201

    token = login_user(client, 'ped@example.com', 'secret123').json()['access_token']

    placement = client.post(
        '/pedagogy/placement',
        headers=auth_header(token),
        json={
            'sentence_complexity': 0.35,
            'vocabulary_variety': 0.4,
            'error_frequency': 0.3,
            'tense_control': 0.45,
            'autonomy': 0.5,
            'clarity': 0.52,
        },
    )
    assert placement.status_code == 200
    assert placement.json()['estimated_level'] in {'A1', 'A2', 'B1', 'B2', 'C1'}

    dashboard = client.get('/pedagogy/dashboard', headers=auth_header(token))
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert 'estimated_level' in data
    assert 'next_step' in data
    assert 'track_progress' in data


def test_mistake_logging_and_recommendations(client, db_session):
    ensure_pedagogical_seed(db_session)

    register_user(client, 'Err', 'err@example.com', 'secret123')
    token = login_user(client, 'err@example.com', 'secret123').json()['access_token']

    mistake = client.post(
        '/pedagogy/mistakes',
        headers=auth_header(token),
        json={
            'user_text': 'Yesterday I goed to work',
            'corrected_text': 'Yesterday I went to work',
            'error_type': 'tense',
            'explanation': 'Use went for past of go',
            'severity': 3,
            'context_feature': 'chat',
        },
    )
    assert mistake.status_code == 200
    assert mistake.json()['error_type'] == 'tense'

    recommendations = client.get('/pedagogy/recommendations', headers=auth_header(token))
    assert recommendations.status_code == 200
    assert len(recommendations.json()) >= 1


def test_vocabulary_review_queue(client, db_session):
    ensure_pedagogical_seed(db_session)

    register_user(client, 'Vocab', 'vocab@example.com', 'secret123')
    token = login_user(client, 'vocab@example.com', 'secret123').json()['access_token']

    queue = client.get('/pedagogy/review-queue', headers=auth_header(token))
    assert queue.status_code == 200

    review = client.post('/pedagogy/vocabulary/review', headers=auth_header(token), json={'item_id': 1, 'correct': True})
    assert review.status_code == 200
    assert review.json()['status'] in {'learning', 'review', 'mastered', 'new'}


def test_free_vs_pro_locked_recommendation(client, db_session):
    ensure_pedagogical_seed(db_session)

    res = register_user(client, 'FreeRec', 'freerec@example.com', 'secret123')
    user_id = res.json()['id']
    token = login_user(client, 'freerec@example.com', 'secret123').json()['access_token']

    placement = client.post(
        '/pedagogy/placement',
        headers=auth_header(token),
        json={
            'sentence_complexity': 0.92,
            'vocabulary_variety': 0.9,
            'error_frequency': 0.05,
            'tense_control': 0.9,
            'autonomy': 0.88,
            'clarity': 0.9,
        },
    )
    assert placement.status_code == 200

    # Keep FREE
    recs_free = client.get('/pedagogy/recommendations', headers=auth_header(token))
    assert recs_free.status_code == 200
    assert any(item.get('locked_for_free') is True for item in recs_free.json())

    # Upgrade to PRO and compare lock distribution
    patch = client.patch(f'/users/{user_id}', json={'plan': 'PRO'})
    assert patch.status_code == 200
    token_pro = login_user(client, 'freerec@example.com', 'secret123').json()['access_token']
    recs_pro = client.get('/pedagogy/recommendations', headers=auth_header(token_pro))
    assert recs_pro.status_code == 200
    assert all(item.get('locked_for_free') is False for item in recs_pro.json())
