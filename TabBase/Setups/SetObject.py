import TabBase.Setups.BaseSettings as Bs
import TabBase.Setups.RequestTypes as Rtp
from datetime import date, timedelta
import plotly.graph_objects as go


def active(db_col: str):
    def request_create(attrs: list, divs: list, regs: list, cities: list, shops: list, old: Bs.OldSign,
                       beg_int: int, end_int=None):
        table = Bs.CART_TABLE if db_col == Bs.CART_COL else Bs.DATA_TABLE
        expr = f"COUNT(DISTINCT {db_col})"
        pos_sales = f"{Bs.SALES_COL} > 0" if db_col == Bs.SHOP_ID_COL else None
        if not end_int:
            date_expr = f"{Bs.DATE_COL} = {beg_int}"
        else:
            date_expr = f"{Bs.DATE_COL} >= {beg_int} and {Bs.DATE_COL} <= {end_int}"
        return Rtp.SimpleByMultiples(attrs=attrs, expressions=[expr], divs=divs, regs=regs, cities=cities, shops=shops,
                                     old_attr=old, date_expr=date_expr, positive_sales=pos_sales, table=table)
    request_create.__name__ = f"{active.__name__}_{db_col}"
    return request_create


def flow(db_col: str, coming=True):
    def request_create(attrs: list, divs: list, regs: list, cities: list, shops: list, old: Bs.OldSign,
                       beg_int: int, end_int=None):
        if db_col == Bs.CART_COL:
            if coming:
                table, sec_table = Bs.ACCUMULATE_TABLE, Bs.ACCUMULATE_TABLE
            else:
                table, sec_table = Bs.LOST_TABLE, Bs.LOST_TABLE
        else:
            table, sec_table = Bs.DATA_TABLE, Bs.DATA_TABLE
        sign = "<" if coming else ">"
        expr = f"COUNT({db_col})"
        pos_sales = f"{Bs.SALES_COL} > 0" if db_col == Bs.SHOP_ID_COL else None
        if coming or not end_int:
            sec_int = beg_int
        else:
            sec_int = end_int
        if not end_int:
            date_expr = f"{Bs.DATE_COL} = {beg_int}"
        else:
            date_expr = f"{Bs.DATE_COL} >= {beg_int} and {Bs.DATE_COL} <= {end_int}"
        sec_date_expr = f"{Bs.DATE_COL} {sign} {sec_int}"

        return Rtp.set_except_request(attrs=attrs, outer_expr=expr, upper_inner_expr=db_col, lower_inner_expr=db_col,
                                      divs=divs, regs=regs, cities=cities, shops=shops, old_attr=old,
                                      positive_sales=pos_sales, date_expr_one=date_expr, date_expr_two=sec_date_expr,
                                      upper_table=table, lower_table=sec_table)
    request_create.__name__ = f"{flow.__name__}_{db_col}_coming_{coming}"
    return request_create


def for_one_cart(db_col: str):
    def request_create(attrs: list, divs: list, regs: list, cities: list, shops: list, old: Bs.OldSign,
                       beg_int: int, end_int=None):
        upper_inner_expr = f"SUM({db_col})"
        lower_inner_expr = f'COUNT(DISTINCT {Bs.CART_COL})'
        if not end_int:
            date_expr = f"{Bs.DATE_COL} = {beg_int}"
        else:
            date_expr = f"{Bs.DATE_COL} >= {beg_int} and {Bs.DATE_COL} <= {end_int}"
        return Rtp.joined_request(attrs=attrs, upper_inner_expr=upper_inner_expr, lower_inner_expr=lower_inner_expr,
                                  divs=divs, regs=regs, cities=cities, shops=shops, old_attr=old,
                                  date_expr=date_expr, upper_table=Bs.DATA_TABLE, lower_table=Bs.CART_TABLE)
    request_create.__name__ = f"{for_one_cart.__name__}_{db_col}"
    return request_create


class Discrete:
    __slots__ = ['label', 'for_one', 'percent', 'plot', 'request_obj', "flowing", "come"]

    def __init__(self, label: str, for_one: bool, percent: bool, plot, request_obj: str, flowing: bool, come: bool):
        self.label = label
        self.for_one = for_one
        self.percent = percent
        self.plot = plot
        self.request_obj = request_obj
        self.flowing = flowing
        self.come = come


DISCRETE = {'shops_act': Discrete(label='5.1 Кол-во магазинов', for_one=False, percent=False, plot=go.Bar,
                                  request_obj=active(Bs.SHOP_ID_COL), flowing=False, come=False),
            'shops_new': Discrete(label='5.2 Новых магазинов', for_one=False, percent=False, plot=go.Bar,
                                  request_obj=flow(Bs.SHOP_ID_COL, coming=True),
                                  flowing=True, come=True),
            'shops_lst': Discrete(label='5.3 Закрытых магазинов', for_one=False, percent=False, plot=go.Bar,
                                  request_obj=flow(Bs.SHOP_ID_COL, coming=False),
                                  flowing=True, come=False),
            'cart_act': Discrete(label='6.1 Активных карт', for_one=False, percent=False, plot=go.Scatter,
                                 request_obj=active(Bs.CART_COL), flowing=False, come=False),
            'cart_new': Discrete(label='6.2 Новых карт', for_one=False, percent=False, plot=go.Scatter,
                                 request_obj=flow(Bs.CART_COL, coming=True), flowing=True, come=True),
            'cart_lst': Discrete(label='6.3 Карт, далее неактивных', for_one=False, percent=False, plot=go.Scatter,
                                 request_obj=flow(Bs.CART_COL, coming=False),
                                 flowing=True, come=False),
            'crt_one_sls': Discrete(label='6.4 Выручка на карту', for_one=True, percent=False, plot=go.Bar,
                                    request_obj=for_one_cart('sales_carts'), flowing=False, come=False),
            'crt_one_chk': Discrete(label='6.5 Чеков на карту', for_one=True, percent=False, plot=go.Bar,
                                    request_obj=for_one_cart('checks_carts_qnt'), flowing=False, come=False)}

DISCRETE_CHECK_LIST = {val.label: key for key, val in DISCRETE.items()}


if __name__ == "__main__":
    import sqlite3
    import os.path

    _up_folder = os.path.split(os.path.dirname(__file__))[0]
    DB = os.path.join(os.path.split(_up_folder)[0], "Database\\summary.db")
    con = sqlite3.connect(DB)

    attr, dvs, rgs, cts, shp, dtt = [], [], [], [], [], ""
    bg_int, ed_int = 60, None
    for num, discrete in enumerate(DISCRETE.values(), start=1):
        req = discrete.request_obj(attr, dvs, rgs, cts, shp, dtt, bg_int, ed_int).request()
        print(num, discrete.label, con.execute(req).fetchone()[0])

    attr, dvs, rgs, cts, shp, dtt = ["div_id"], [], [], [], [], ""
    bg_int, ed_int = 0, 31
    for num, discrete in enumerate(DISCRETE.values(), start=1):
        req = discrete.request_obj(attr, dvs, rgs, cts, shp, dtt, bg_int, ed_int).request()
        for ln in con.execute(req):
            print(num, discrete.label, *ln)
    con.close()
