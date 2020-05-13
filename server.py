from oauth_web_api import OauthWebAPI
import json
import database.db_queries as db

from flask import request
from flask_cors import CORS
from flask_api import FlaskAPI, status

app = FlaskAPI(__name__)
CORS(app)


@app.route("/<string:shop>/<string:cart_id>/<int:score>", methods=['POST'])
def category_game_finished_add_to_cart(shop, cart_id, score):
    shop_id, res_owner_key, res_owner_secret, client_key, client_secret, coupon_code_id = \
        get_code_id_corresponding_to_score(request.environ['HTTP_ORIGIN'], shop, score)
    if coupon_code_id is not None:
        m2_api = OauthWebAPI(res_owner_key, res_owner_secret, client_key, client_secret)
        coupon = get_coupon_for_cart_id(cart_id, m2_api, coupon_code_id, shop_id, score)
        return check_valid_coupon(coupon, m2_api, cart_id, shop_id)
    else:
        return json.dumps({"code": "not allowed"}), status.HTTP_403_FORBIDDEN


@app.route("/<string:shop>/coupon/<string:cart_id>", methods=['GET'])
def get_coupon_in_cart(shop, cart_id):
    shop_id, res_owner_key, res_owner_secret, client_key, client_secret = \
        get_shop_data(shop, request.environ['HTTP_ORIGIN'])
    if shop_id is not None:
        m2_api = OauthWebAPI(res_owner_key, res_owner_secret, client_key, client_secret)
        coupon_code = check_cart_id_for_coupon(cart_id, shop_id, m2_api)
        if coupon_code is not None:
            return json.dumps({"cart_coupon": str(coupon_code)}), status.HTTP_409_CONFLICT
        else:
            return json.dumps({"cart_coupon": "empty"}), status.HTTP_200_OK
    else:
        return json.dumps({"code": "not allowed"}), status.HTTP_403_FORBIDDEN


def add_coupon_to_cart(m2_api, coupon, cart_id, shop_id):
    if m2_api.added_coupon_to_cart(cart_id, coupon):
        insert_coupon_with_cart_id_in_db(cart_id, shop_id, coupon)
        return True
    else:
        insert_coupon_with_cart_id_in_db(cart_id, shop_id, coupon, False)
        return False


def get_code_id_corresponding_to_score(origin, shop_id, score):
    return db.get_coupon_id_webshop(origin, shop_id, score)


def get_coupon_for_cart_id(cart_id, m2_api, coupon_code_id, shop_id, score):
    generated_coupon = check_cart_id_for_coupon(cart_id, shop_id, m2_api)
    if generated_coupon is not None:
        return generated_coupon
    else:
        insert_score_in_db(score, shop_id)
        return m2_api.send_coupon_request(coupon_code_id)


def get_shop_data(shop, origin):
    return db.select_shop_info(origin, shop)


def check_cart_id_for_coupon(cart_id, shop, m2_api):
    if cart_id.isdigit():
        coupon_in_user_cart = m2_api.get_coupon_in_cart(cart_id)
        if coupon_in_user_cart == b'[]':
            return None
        else:
            return coupon_in_user_cart
    return db.select_coupon_with_cart_id(cart_id, shop)


def check_valid_coupon(coupon, m2_api, cart_id, shop_id):
    if coupon is None:
        return json.dumps({"code": "Not Allowed"}), status.HTTP_403_FORBIDDEN
    elif isinstance(coupon, str):
        if add_coupon_to_cart(m2_api, coupon, cart_id, shop_id):
            return json.dumps({"code": "added"}), status.HTTP_201_CREATED
        else:
            return json.dumps({"code": str(coupon)}), status.HTTP_200_OK
    else:
        return json.dumps({"code": str(coupon[0])}), status.HTTP_200_OK


def insert_score_in_db(score, shop_id):
    db.insert_score_with_shop(score, shop_id)


def insert_coupon_with_cart_id_in_db(cart_id, shop, coupon_code, added=True):
    db.insert_cart_id_with_coupon(cart_id, shop, coupon_code, added)


if __name__ == "__main__":
    app.run(debug=True)
