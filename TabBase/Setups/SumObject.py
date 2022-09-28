import plotly.graph_objects as go


class United:
    __slots__ = ['label', 'for_one', 'percent', 'plot', 'calculated']

    def __init__(self, label: str, for_one: bool, percent: bool, plot, calculated):
        self.label = label
        self.for_one = for_one
        self.percent = percent
        self.plot = plot
        self.calculated = calculated


UNITED = {'sales_totals': United(label='1.1 Выручка', for_one=False, percent=False, plot=go.Scatter,
                                 calculated='SUM(sales) as sales_totals'),
          'sales_not_bn': United(label='1.2 Выручка без бонусов', for_one=False, percent=False, plot=go.Scatter,
                                 calculated='SUM(sales_not_bonus) as sales_not_bn'),
          'sales_carts': United(label='1.3 Выручка по картам', for_one=False, percent=False, plot=go.Scatter,
                                calculated='SUM(sales_carts) as sales_carts'),
          'part_crt_sls': United(label='1.4 Доля карт в выручке', for_one=True, percent=True, plot=go.Bar,
                                 calculated='SUM(sales_carts) / SUM(sales) as part_crt_sls'),
          'part_bon_sls': United(label='1.5 Доля бонусов в выручке', for_one=True, percent=True, plot=go.Bar,
                                 calculated='SUM(sales) / SUM(sales_not_bonus) - 1 as part_bon_sls'),
          'gross_profit': United(label='2.1 Валовая прибыль', for_one=False, percent=False, plot=go.Scatter,
                                 calculated='SUM(sales_not_bonus) - SUM(cost_price) as gross_profit'),
          'margin_profit': United(label='2.2 Маржин-ая прибыль', for_one=False, percent=False, plot=go.Scatter,
                                  calculated='SUM(sales_not_bonus) - SUM(cost_price) - SUM(woff) as margin_profit'),
          'woff': United(label='2.3 Списания', for_one=False, percent=False, plot=go.Scatter,
                         calculated='SUM(woff) as woff'),
          'markup': United(label='2.4 Наценка без бон-в', for_one=True, percent=True, plot=go.Bar,
                           calculated='SUM(sales_not_bonus) / SUM(cost_price) - 1 as markup'),
          'margin': United(label='2.5 Маржин-ть без бон-в', for_one=True, percent=True, plot=go.Bar,
                           calculated='(SUM(sales_not_bonus) - SUM(woff)) / SUM(cost_price) - 1 as margin'),
          'count_checks': United(label='3.1 Кол-во чеков', for_one=False, percent=False, plot=go.Scatter,
                                 calculated='SUM(checks_qnt) as count_checks'),
          'count_crt_chk': United(label='3.2 Кол-во чеков по картам', for_one=False, percent=False, plot=go.Scatter,
                                  calculated='SUM(checks_carts_qnt) as count_crt_chk'),
          'part_crt_chk': United(label='3.3 Доля карт в чеках', for_one=True, percent=True, plot=go.Bar,
                                 calculated='SUM(checks_carts_qnt) / SUM(checks_qnt) as part_crt_chk'),
          'middle_check': United(label='3.4 Средний чек', for_one=True, percent=False, plot=go.Bar,
                                 calculated='SUM(sales) / SUM(checks_qnt) as middle_check'),
          'middle_crt_chk': United(label='3.5 Средний чек по картам', for_one=True, percent=False, plot=go.Bar,
                                   calculated='SUM(sales_carts) / SUM(checks_carts_qnt) as middle_crt_chk'),
          'count_beer': United(label='4.1 Пиво разливное, литры', for_one=False, percent=False, plot=go.Scatter,
                               calculated='SUM(beer_ltr) as count_beer'),
          'count_beer_kz': United(label='4.2 Пиво Канцлер, литры', for_one=False, percent=False, plot=go.Scatter,
                                  calculated='SUM(beer_kz_ltr) as count_beer_kz')}

UNITED_CHECK_LIST = {val.label: key for key, val in UNITED.items()}


if __name__ == "__main__":
    import sqlite3
    import os.path

    bool_set = set()
    for key, meta in UNITED.items():
        bool_set.add(key == meta.calculated.split(" as ")[-1])
    print("Ключи == псевдонимам sql выражения", bool_set)

    _up_folder = os.path.split(os.path.dirname(__file__))[0]
    DB = os.path.join(os.path.split(_up_folder)[0], "Database\\summary.db")
    con = sqlite3.connect(DB)
    for num, meta in enumerate(UNITED.values(), start=1):
        val = con.execute(f"SELECT {meta.calculated} FROM data").fetchone()[0]
        print(num, "  ", meta.label, "  ", val)
    con.close()
