import random
import sqlite3
import os.path
from datetime import date, timedelta
from time import time
from collections import namedtuple


def time_meter(func):
    def wrapper():
        st = time()
        func()
        print(f"Время выполнения - {round(time() - st, 1)} сек.")
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def _months_range(end: date) -> list:
    temp = date(2020, 1, 1)
    result = [temp]
    while True:
        temp = date(temp.year, temp.month + 1, 1) if temp.month + 1 <= 12 else date(temp.year + 1, 1, 1)
        result.append(temp)
        if temp.year == end.year and temp.month == end.month:
            break
    return result


def _request_for_inserting(cursor, table_name: str) -> str:
    pragma = f"PRAGMA table_info({table_name})"
    cols_count = len(cursor.execute(pragma).fetchall())
    placeholder = f"({','.join(['?'] * cols_count)})"
    return f"INSERT INTO {table_name} VALUES {placeholder}"


@time_meter
def creation():
    divisions = {i: f"Дивизион{i}" for i in range(1, random.randint(3, 5))}
    regions = {i: f"Регион{i}" for i in range(1, random.randint(10, 20))}
    cities = {i: f"НасПункт{i}" for i in range(1, random.randint(30, 50))}
    div_ids, reg_ids, city_ids = list(divisions.keys()), list(regions.keys()), list(cities.keys())

    Requisites = namedtuple("Requisites", ["div_name", "reg_name", "city_name", "div_id", "reg_id", "city_id",
                                           "old_shop", "shop_name"])
    shops = dict()
    for shop_id in range(1, random.randint(100, 200)):
        did = random.choice(div_ids)
        rid = random.choice(reg_ids)
        cid = random.choice(city_ids)
        old = random.choice([0, 1])
        shops[shop_id] = Requisites(divisions[did], regions[rid], cities[cid], did, rid, cid, old, f"Магазин{shop_id}")
    shop_ids = list(shops.keys())
    old_shops_ids = list([k for k, val in shops.items() if val.old_shop == 1])
    not_old_shops_ids = list(set(shop_ids).difference(set(old_shops_ids)))

    up_folder = os.path.split(os.path.dirname(__file__))[0]
    db_cache_graph = os.path.join(up_folder, "Database\\cache_graph.db")
    con_cache_graph = sqlite3.connect(db_cache_graph)
    db_cache_table = os.path.join(up_folder, "Database\\cache_table.db")
    con_cache_table = sqlite3.connect(db_cache_table)
    db_app = os.path.join(up_folder, "Database\\summary.db")
    con_app = sqlite3.connect(db_app)
    cur_app = con_app.cursor()

    schema_cache_graph = open(os.path.join(up_folder, "Database\\schema_cache_graph.sql"), encoding="utf8")
    con_cache_graph.executescript(schema_cache_graph.read())
    schema_cache_table = open(os.path.join(up_folder, "Database\\schema_cache_table.sql"), encoding="utf8")
    con_cache_table.executescript(schema_cache_table.read())
    con_cache_graph.close()
    con_cache_table.close()
    schema = open(os.path.join(up_folder, "Database\\schema_summary.sql"), encoding="utf8")
    cur_app.executescript(schema.read())

    request = _request_for_inserting(cur_app, table_name="tt")
    for shop_id, ln in shops.items():
        cur_app.execute(request, (*ln, shop_id))
    print("Справочники магазинов и последних дат записаны.")

    last_proc_date = date(2022, random.randint(1, 12), random.randint(1, 28))
    last_roz_date = date(2022, random.randint(1, 12), 1)
    date_range = _months_range(max(last_proc_date, last_roz_date))
    date_range_integers = [(dt - date(2020, 1, 1)).days for dt in date_range]
    for dt in date_range_integers:
        cur_app.execute("INSERT INTO dates_integers VALUES (?)", (dt,))
    print("Перечень дат записан в базу приложения.")

    carts_accumulate = set()
    request_data = _request_for_inserting(cur_app, table_name="data")
    request_carts = _request_for_inserting(cur_app, table_name="carts")
    request_carts_accumulate = _request_for_inserting(cur_app, table_name="carts_accumulate")
    for dt_int in date_range_integers:
        carts = set()
        chosen_shops = old_shops_ids.copy()
        shops_qnt = random.randint(len(not_old_shops_ids) // 2, len(not_old_shops_ids))
        for i in range(shops_qnt):
            chosen_shops.append(random.choice(not_old_shops_ids))

        for shop_id in chosen_shops:
            sales = random.randint(150000, 3000000)
            sales_carts = sales * random.uniform(0.6, 0.95)
            chk_qnt = sales / random.randint(300, 500)
            chk_qnt_carts = chk_qnt * random.uniform(0.7, 0.95)
            sales_not_bonus = sales * random.uniform(0.8, 0.99)
            cost_price = sales_not_bonus / random.uniform(1.3, 1.7)
            woff = sales_not_bonus * random.uniform(0.01, 0.01)
            beer_ltr = sales * random.uniform(0.4, 0.6) / random.uniform(90, 110)
            beer_kz_ltr = beer_ltr * random.uniform(0.9, 0.99)
            row = (dt_int, shops[shop_id].div_id, shops[shop_id].reg_id, shops[shop_id].city_id,
                   shop_id, shops[shop_id].old_shop,
                   sales, sales_carts, chk_qnt, chk_qnt_carts, sales_not_bonus, cost_price, woff, beer_ltr, beer_kz_ltr)
            cur_app.execute(request_data, row)

            carts_qnt = random.randint(100, 300)
            for j in range(carts_qnt):
                crt = random.randint(1, 999999)
                carts.add((shops[shop_id].div_id, shops[shop_id].reg_id, shops[shop_id].city_id,
                           shop_id, shops[shop_id].old_shop, crt))

        new_carts = carts.difference(carts_accumulate)
        carts_accumulate.update(new_carts)

        for row in carts:
            cur_app.execute(request_carts, (dt_int, *row))
        for row in new_carts:
            cur_app.execute(request_carts_accumulate, (dt_int, *row))
        carts.clear()
        new_carts.clear()
        del carts
        del new_carts
        print(f"Данные за {(date(2020, 1, 1) + timedelta(dt_int)).strftime('%m.%Y')} записаны.")
    con_app.commit()

    carts_lost = set()
    for dt in reversed(date_range_integers):
        carts = {ln for ln in cur_app.execute("""SELECT div_id, reg_id, city_id, shop_id, old_shop, cart
                                                 FROM carts
                                                 WHERE date_month = ?""", (dt,))}
        lost = carts.difference(carts_lost)
        carts_lost.update(lost)
        for row in lost:
            cur_app.execute("INSERT INTO carts_lost VALUES (?,?,?,?,?,?,?)", (dt, *row))
        print(f"Данные по не активным картам за {(date(2020, 1, 1) + timedelta(dt)).strftime('%m.%Y')}"
              " записаны в базу приложения.")
    con_app.commit()
    con_app.close()
    print("База данных приложения создана.")


if __name__ == "__main__":
    creation()
