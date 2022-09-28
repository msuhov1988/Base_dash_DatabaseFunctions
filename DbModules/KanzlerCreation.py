import sqlite3
import os.path
from datetime import date, timedelta
from collections import namedtuple
import time
import DbModules.KanzlerSupporting as KzSup


def time_meter(func):
    def wrapper():
        st = time.time()
        func()
        print(f"Время выполнения - {round(time.time() - st, 1)} сек.")
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


@time_meter
def creation():
    db_proc = r"C:\Users\suhov\!_DB_project\checks_integers.db"
    con_proc = sqlite3.connect(db_proc)
    cur_proc = con_proc.cursor()
    db_roz = r"C:\Users\suhov\!_DB_project\dash.db"
    con_roz = sqlite3.connect(db_roz)
    cur_roz = con_roz.cursor()
    up_folder = os.path.split(os.path.dirname(__file__))[0]
    db_app = os.path.join(up_folder, "Database\\summary.db")
    con_app = sqlite3.connect(db_app)
    cur_app = con_app.cursor()
    db_cache_graph = os.path.join(up_folder, "Database\\cache_graph.db")
    con_cache_graph = sqlite3.connect(db_cache_graph)
    db_cache_table = os.path.join(up_folder, "Database\\cache_table.db")
    con_cache_table = sqlite3.connect(db_cache_table)

    prime_proc_modified = time.ctime(os.path.getmtime(db_proc))
    prime_roz_modified = time.ctime(os.path.getmtime(db_roz))
    exist_table = cur_app.execute("""SELECT name
                                     FROM sqlite_master
                                     WHERE type='table' AND name = 'last_changes_dates'""").fetchone()
    if exist_table:
        last_dates = cur_app.execute("SELECT proc_date, roz_date FROM last_changes_dates").fetchone()
        if last_dates:
            app_proc_modified, app_roz_modified = last_dates
            if app_proc_modified == prime_proc_modified and app_roz_modified == prime_roz_modified:
                print("Данные первичных баз не изменились.")
                print("Перезапись базы приложения не требуется.")
                return

    print("Создание базы данных...")
    schema_cache_graph = open(os.path.join(up_folder, "Database\\schema_cache_graph.sql"), encoding="utf8")
    con_cache_graph.executescript(schema_cache_graph.read())
    schema_cache_table = open(os.path.join(up_folder, "Database\\schema_cache_table.sql"), encoding="utf8")
    con_cache_table.executescript(schema_cache_table.read())
    con_cache_graph.close()
    con_cache_table.close()

    schema = open(os.path.join(up_folder, "Database\\schema_summary.sql"), encoding="utf8")
    cur_app.executescript(schema.read())
    cur_app.execute("INSERT INTO last_changes_dates VALUES (?,?)", (prime_proc_modified, prime_roz_modified))
    print("Даты изменений первичных баз записаны в базу приложения.")

    last_proc_int = cur_proc.execute("SELECT MAX(date) FROM checks").fetchone()[0]
    last_proc_date = date(2020, 1, 1) + timedelta(last_proc_int)
    year, month = cur_roz.execute("""SELECT year, MAX(month) FROM sales
                                     WHERE year = (SELECT MAX(year) FROM sales)""").fetchone()
    last_roz_date = date(year, month, 1)
    last_max_date = max(last_roz_date, last_proc_date)

    temp_cur, table = (cur_roz, 'sales') if last_proc_date < last_roz_date else (cur_proc, 'checks')
    request = """SELECT mag_id FROM {0} WHERE month = 1 and year = 2020
                 INTERSECT
                 SELECT mag_id FROM {0} WHERE month = ? and year = ?""".format(table)
    old_shops = {ln[0] for ln in temp_cur.execute(request, (last_max_date.month, last_max_date.year))}
    print("Перечень магазинов, работающих с 01.01.2020 получен.")

    divs, regs, cities = set(), set(), set()
    for ln in cur_proc.execute("""SELECT division, region, city FROM tt"""):
        divs.add(ln[0])
        regs.add(ln[1])
        cities.add(ln[2])
    divs, regs, cities = list(divs), list(regs), list(cities)
    divs.sort()
    regs.sort()
    cities.sort()
    divs = {name: num for num, name in enumerate(divs, start=1)}
    regs = {name: num for num, name in enumerate(regs, start=1)}
    cities = {name: num for num, name in enumerate(cities, start=1)}
    Requisites = namedtuple("Requisites", ["div_name", "reg_name", "city_name", "div_id", "reg_id", "city_id",
                                           "old_shop", "shop_name"])
    shops = dict()
    for ln in cur_proc.execute("""SELECT id, division, region, city, name FROM tt"""):
        old = 1 if ln[0] in old_shops else 0
        shops[ln[0]] = Requisites(ln[1], ln[2], ln[3], divs[ln[1]], regs[ln[2]], cities[ln[3]], old, ln[4])

    cols_count = len(cur_app.execute("PRAGMA table_info(tt)").fetchall())
    placeholder = f"({','.join(['?'] * cols_count)})"
    request = f"INSERT INTO tt VALUES {placeholder}"
    for shop_id, ln in shops.items():
        cur_app.execute(request, (*ln, shop_id))
    print("Справочник магазинов записан в базу приложения.")

    date_range = _months_range(last_max_date)
    date_range_integers = [(dt - date(2020, 1, 1)).days for dt in date_range]
    for dt in date_range_integers:
        cur_app.execute("INSERT INTO dates_integers VALUES (?)", (dt,))
    print("Перечень дат записан в базу приложения.")

    carts_accumulate = set()
    for dt in date_range:
        KzSup.collect_and_writing(cur_app, cur_proc, cur_roz, dt, shops, carts_accumulate)
        print(f"Данные за {dt.strftime('%m.%Y')} записаны в базу приложения.")
    con_app.commit()
    con_proc.close()
    con_roz.close()

    carts_lost = set()
    for dt in reversed(date_range):
        dt_int = (dt - date(2020, 1, 1)).days
        carts = {ln for ln in cur_app.execute("""SELECT div_id, reg_id, city_id, shop_id, old_shop, cart
                                                 FROM carts
                                                 WHERE date_month = ?""", (dt_int,))}
        lost = carts.difference(carts_lost)
        carts_lost.update(lost)
        for row in lost:
            cur_app.execute("INSERT INTO carts_lost VALUES (?,?,?,?,?,?,?)", (dt_int, *row))
        print(f"Данные по не активным картам за {dt.strftime('%m.%Y')} записаны в базу приложения.")
    con_app.commit()
    con_app.close()
    print("База данных приложения создана.")


if __name__ == "__main__":
    creation()
