from oauth_web_api import OauthWebAPI
import json
import database.db_queries as db

from flask_cors import CORS
from flask_api import FlaskAPI, status
from flask_restful import Resource, Api

app = FlaskAPI(__name__)
CORS(app)
api = Api(app)


class PostScore(Resource):
    m2_api = None
    shop_id = None
    cart_id = None
    score = 0

    def post(self, shop, cart_id, score):
        self.init_class_variables(cart_id, score)
        shop_info = self.get_code_id_corresponding_to_score(shop)
        if shop_info is not None:
            self.shop_id, res_owner_key, res_owner_secret, client_key, client_secret, coupon_code_id = shop_info
            self.m2_api = OauthWebAPI(
                res_owner_key, res_owner_secret, client_key, client_secret)
            coupon = self.get_coupon_for_cart_id(coupon_code_id)
            return self.check_valid_coupon(coupon)
        else:
            return json.dumps({"code": "Er is iets fout gegaan, probeer het later opnieuw."}), status.HTTP_403_FORBIDDEN

    def init_class_variables(self, cart_id, score):
        self.cart_id = cart_id
        self.score = score

    def get_coupon_for_cart_id(self, coupon_code_id):
        generated_coupon = check_cart_id_for_coupon(
            self.cart_id, self.shop_id, self.m2_api)
        if generated_coupon is not None:
            return generated_coupon
        else:
            self.insert_score_in_db()
            return self.m2_api.send_coupon_request(coupon_code_id)

    def get_code_id_corresponding_to_score(self, shop):
        return db.get_coupon_id_webshop(shop, self.score)

    def check_valid_coupon(self, coupon):
        if coupon is None:
            return json.dumps({"code": "Er is iets fout gegaan, probeer het later opnieuw."}), status.HTTP_403_FORBIDDEN
        elif isinstance(coupon, str):
            if self.add_coupon_to_cart(coupon):
                return json.dumps({
                    "code": "De kortingscode is toegevoegd aan de winkelwagen. "
                    "Druk op volgende om verder te gaan."}), status.HTTP_201_CREATED
            else:
                return json.dumps({"code": "Gewonnen couponcode is: " + str(coupon)}), status.HTTP_200_OK
        else:
            return json.dumps({"code": "Gewonnen couponcode is: " + str(coupon[0])}), status.HTTP_200_OK

    def add_coupon_to_cart(self, coupon):
        if self.m2_api.added_coupon_to_cart(self.cart_id, coupon):
            self.insert_coupon_with_cart_id_in_db(coupon)
            return True
        else:
            self.insert_coupon_with_cart_id_in_db(coupon, False)
            return False

    def insert_coupon_with_cart_id_in_db(self, coupon_code, added=True):
        db.insert_cart_id_with_coupon(
            self.cart_id, self.shop_id, coupon_code, added)

    def insert_score_in_db(self):
        db.insert_score_with_shop(self.score, self.shop_id)


class GetCouponInCart(Resource):
    def get(self, shop, cart_id):
        shop_info = get_shop_data(shop)
        if shop_info is not None:
            shop_id, res_owner_key, res_owner_secret, client_key, client_secret = shop_info
            m2_api = OauthWebAPI(
                res_owner_key, res_owner_secret, client_key, client_secret)
            coupon_code = check_cart_id_for_coupon(cart_id, shop_id, m2_api)
            if coupon_code is not None:
                return json.dumps({"response_text": "Er zit al een coupon in de winkelwagen. Game "
                                   "spelen voor korting is niet mogelijk."}), status.HTTP_409_CONFLICT
            else:
                return json.dumps({"response_text": "empty"}), status.HTTP_200_OK
        else:
            return json.dumps({"response_text": "Er is iets fout gegaan. Probeer het later opnieuw"}), status.HTTP_403_FORBIDDEN


api.add_resource(PostScore, '/<string:shop>/<string:cart_id>/<int:score>')
api.add_resource(GetCouponInCart, '/<string:shop>/coupon/<string:cart_id>')


def check_cart_id_for_coupon(cart_id, shop, m2_api):
    if cart_id.isdigit():
        coupon_in_user_cart = m2_api.get_coupon_in_cart(cart_id)
        if coupon_in_user_cart == b'[]':
            return None
        else:
            return coupon_in_user_cart
    return db.select_coupon_with_cart_id(cart_id, shop)


def get_shop_data(shop):
    return db.select_shop_info(shop)


if __name__ == "__main__":
    app.run(debug=True)
