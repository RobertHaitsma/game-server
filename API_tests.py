import requests
from oauth_web_api import OauthWebAPI

m2_api = OauthWebAPI('rtxojvqglcd2m4f8n3pg6nhi1dviil00', 'bhzrf9y224nc2rlonf5z6urr0499n8ih',
                     'm748bxohupsrer5hqvaynfkhy8nlpyz8', 'zz2z4zowvgyujqf38wcnzb0koqch7rx4')

cart_id = 20


def test_game_finished_coupon_added_to_cart():
    response = requests.post('http://localhost:3000/didi/500/20')
    assert response.status_code == 201


def test_cart_id_and_coupon_added_in_db():
    assert db.get_coupon_with_cart_id(cart_id) is not None


def test_coupon_code_in_cart():
    assert m2_api.get_coupon_in_cart(20) is not None


def test_category_game_finished_add_to_cart_wrong_category_response_405():
    response = requests.post('http://localhost:3000/didi/500/20')
    assert response.status_code == 405


def test_category_game_finished_add_to_cart_low_score_response_204():
    response = requests.post('http://localhost:3000/didi/1/20')
    assert response.status_code == 204


def test_category_game_finished_add_to_cart_low_score_response_20():
    response = requests.post('http://localhost:3000/didi/1/20')
    assert response.status_code == 204


def test_category_game_finished_add_to_cart_coupon_added_to_cart():
    response = requests.post('http://localhost:3000/didi/500/20')
    cart_items = m2_api.getCartItems('20')
    assert cart_items.currency
