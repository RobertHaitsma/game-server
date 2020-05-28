from database import db_connection


def get_coupon_id_webshop(shop, score):
    conn = db_connection.get_connection()
    cursor = conn.cursor()

    shop_data = select_shop_info(shop)

    if shop_data is None:
        return None
    else:
        catalog_coupon_id = select_catalog_coupon_id_with_score(
            cursor, shop_data[0], score)

    db_connection.close_connection(conn)

    if catalog_coupon_id is not None:
        return shop_data + catalog_coupon_id
    else:
        return None


def select_shop_info(shop):
    conn = db_connection.get_connection()
    cursor = conn.cursor()
    get_shop = ("SELECT id, resource_owner_key, resource_owner_secret, client_key, client_secret "
                "FROM shop "
                "WHERE name = %(shop)s")

    cursor.execute(get_shop, {'shop': shop})
    shop_data = cursor.fetchone()

    return shop_data


def select_catalog_coupon_id_with_score(cursor, shop_id, score):
    get_catalog_coupon_id = ("SELECT catalog_coupon_id "
                             "FROM available_code "
                             "WHERE shop_id = %s AND active = 1 AND %s BETWEEN min_score AND max_score")

    coupon_info = (shop_id, score)
    cursor.execute(get_catalog_coupon_id, coupon_info)
    catalog_coupon_id = cursor.fetchone()
    if catalog_coupon_id is not None:
        return catalog_coupon_id
    else:
        return None


def select_coupon_with_cart_id(cart_id, shop_id):
    conn = db_connection.get_connection()
    cursor = conn.cursor()

    get_couponcode = ("SELECT coupon_code "
                      "FROM used_cart "
                      "WHERE cart_id = %s AND shop_id = %s")

    cart_shop_id = (cart_id, shop_id)
    cursor.execute(get_couponcode, cart_shop_id)
    coupon_code = cursor.fetchone()

    db_connection.close_connection(conn)

    if coupon_code is not None:
        return coupon_code
    else:
        return None


def insert_score_with_shop(score, shop_id):
    conn = db_connection.get_connection()
    cursor = conn.cursor()
    print(score, shop_id)
    insert_score = ("INSERT INTO high_score (score, shop_id) "
                    "VALUES (%s, %s)")
    insert_values = (score, shop_id)

    cursor.execute(insert_score, insert_values)
    db_connection.close_insert_connection(conn)


def insert_cart_id_with_coupon(cart_id, shop_id, coupon_code, automatic_added):
    conn = db_connection.get_connection()
    cursor = conn.cursor()
    print(cart_id, coupon_code)

    insert_cart_id = ("INSERT INTO used_cart (cart_id, shop_id, coupon_code, automatic_added)"
                      "VALUES (%s, %s, %s, %s)")
    insert_values = (cart_id, shop_id, coupon_code, automatic_added)

    cursor.execute(insert_cart_id, insert_values)
    db_connection.close_insert_connection(conn)
