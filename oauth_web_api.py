import requests
import json
from requests_oauthlib import OAuth1


class OauthWebAPI:
    base_request_url = 'http://127.0.0.1:8080/rest/V1/'

    def __init__(self, res_owner_key, res_owner_secret, client_key, client_secret):
        self.resource_owner_key = res_owner_key
        self.resource_owner_secret = res_owner_secret
        self.client_key = client_key
        self.client_secret = client_secret
        self.oauth = OAuth1(client_key=client_key, client_secret=client_secret, resource_owner_key=res_owner_key,
                            resource_owner_secret=res_owner_secret)

    def send_coupon_request(self, coupon_code_id):
        payload = json.dumps({
            "couponSpec": {
                "rule_id": coupon_code_id,
                "format": "",
                "quantity": 1,
                "length": 12,
                "prefix": "",
                "suffix": "",
                "delimiter_at_every": 0,
                "delimiter": "",
                "extension_attributes": {}
            }
        })

        coupon_link = 'coupons/generate'
        request_token_url = self.base_request_url + coupon_link

        response = requests.post(url=request_token_url, auth=self.oauth, data=payload,
                                 headers={'Content-Type': 'application/json'})
        coupon = response.content.decode('utf-8')

        if response.status_code == 200:
            return coupon[2:-2]
        else:
            return None

    def added_coupon_to_cart(self, cart_id, coupon_code):
        if cart_id.isdigit():
            request_token_url = self.base_request_url + \
                'carts/' + cart_id + '/coupons/' + coupon_code
        else:
            request_token_url = self.base_request_url + \
                'guest-carts/' + cart_id + '/coupons/' + coupon_code

        response = requests.put(url=request_token_url, auth=self.oauth, headers={
                                'Content-Type': 'application/json'})

        return response.status_code == 200

    def get_coupon_in_cart(self, cart_id):
        request_token_url = self.base_request_url + 'carts/' + cart_id + '/coupons'

        response = requests.get(url=request_token_url, auth=self.oauth, headers={
                                'Content-Type': 'application/json'})
        if response.status_code == 200:
            return response.content
        else:
            return None

    def get_cart_items(self, cart_id):
        request_token_url = self.base_request_url + 'carts/' + cart_id

        response = requests.get(url=request_token_url, auth=self.oauth, headers={
                                'Content-Type': 'application/json'})
        if response.status_code == 200:
            return response.content
        else:
            return None
