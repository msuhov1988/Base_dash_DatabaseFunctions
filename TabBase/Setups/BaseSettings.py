import os.path
import sqlite3
from enum import Enum
from datetime import date, timedelta
from collections import namedtuple


# enums whose values used in the layout
class OldSign(Enum):
    old_only = "ДТТ"
    anyone = ""


class ForOneSign(Enum):
    for_one = "НА ТТ"
    anyone = ""


class LineType(Enum):
    chronic = "chronic"
    years = "years"


# constants involved in functions and expressions
DATA_TABLE = "data"
CART_TABLE = "carts"
ACCUMULATE_TABLE = "carts_accumulate"
LOST_TABLE = "carts_lost"
DB_OLD_SIGN = 1
OLD_SHOP_COL = "old_shop"
DATE_COL = "date_month"
DIV_ID_COL = "div_id"
REG_ID_COL = "reg_id"
CITY_ID_COL = "city_id"
SHOP_ID_COL = "shop_id"
CART_COL = "cart"
SALES_COL = "sales"


# keys - columns of database
TABLE_SLICES = {DIV_ID_COL: "Дивизион",
                REG_ID_COL: "Регион",
                CITY_ID_COL: "Нас.пункт",
                SHOP_ID_COL: "Магазин"}

_up_folder = os.path.split(os.path.dirname(__file__))[0]
DB = os.path.join(os.path.split(_up_folder)[0], "Database\\summary.db")


def dates_of_database():
    con_app = sqlite3.connect(DB)
    cur_app = con_app.cursor()
    dates_integers = [ln[0] for ln in cur_app.execute("SELECT date_int FROM dates_integers")]
    con_app.close()
    dates_integers.sort()
    return dates_integers


def references():
    con = sqlite3.connect(DB)
    ref_line = namedtuple("ref_line", "division region city shop")
    refers = set()
    divs, regs, cities, shops = dict(), dict(), dict(), dict()
    name_trans = {".": "", ",": "", ":": "", ";": ""}
    for ln in con.execute(f"""SELECT {DIV_ID_COL}, {REG_ID_COL}, {CITY_ID_COL}, {SHOP_ID_COL},
                                     division, region, city, shop
                              FROM tt
                              GROUP BY {DIV_ID_COL}, {REG_ID_COL}, {CITY_ID_COL}, {SHOP_ID_COL}"""):
        refers.add(ref_line(*ln[:4]))
        divs[ln[0]] = ln[4].translate(name_trans)
        regs[ln[1]] = ln[5].translate(name_trans)
        cities[ln[2]] = ln[6].translate(name_trans)
        shops[ln[3]] = ln[7].translate(name_trans)
        divs = {k: divs[k] for k in sorted(divs, reverse=True)}
        regs = {k: regs[k] for k in sorted(regs)}
        cities = {k: cities[k] for k in sorted(cities)}
        shops = {k: shops[k] for k in sorted(shops)}
    names_comparison = {DIV_ID_COL: divs,
                        REG_ID_COL: regs,
                        CITY_ID_COL: cities,
                        SHOP_ID_COL: shops}   # keys - columns of database
    con.close()
    return refers, divs, regs, cities, shops, names_comparison
