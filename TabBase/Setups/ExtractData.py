import TabBase.Setups.BaseSettings as Bs
from .RequestTypes import SimpleBySingle, SimpleByMultiples
from .CacheRequests import cache_graph_extract, cache_graph_insert, cache_table_extract, cache_table_insert
from .SumObject import UNITED
from .SetObject import DISCRETE
import sqlite3
import os.path
from datetime import date, timedelta
from collections import defaultdict, namedtuple
from threading import Thread, Lock


class Connect:
    def __init__(self, database_path):
        self.database = database_path
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.database)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            self.connection.close()


_up_folder = os.path.split(os.path.dirname(__file__))[0]
DB = os.path.join(os.path.split(_up_folder)[0], "Database\\summary.db")
DB_CACHE_GRAPH = os.path.join(os.path.split(_up_folder)[0], "Database\\cache_graph.db")
DB_CACHE_TABLE = os.path.join(os.path.split(_up_folder)[0], "Database\\cache_table.db")
UNITED_KEYS = set(UNITED.keys())
ACTIVE_SHOPS_KEY = 'shops_act'
Result = namedtuple("Result", ["total", "for_one"])


def _in_thread_graph_set(disc_arg: str, divs: list, regs: list, cities: list, shops: list, old: Bs.OldSign,
                         dates_int_range: list, result: defaultdict, date_int: int, lock: Lock):
    flowing, come = DISCRETE[disc_arg].flowing, DISCRETE[disc_arg].come
    if flowing and come and date_int == dates_int_range[0]:
        return
    elif flowing and not come and date_int == dates_int_range[-1]:
        return
    dt = date(2020, 1, 1) + timedelta(days=date_int)
    cache_request = cache_graph_extract(divs=divs, regs=regs, cities=cities, shops=shops, old_attr=old,
                                        date_int=date_int, mark_argument=disc_arg)
    with Connect(DB_CACHE_GRAPH) as con_cache:
        try:
            local_result_tuple = con_cache.execute(cache_request).fetchone()
        except sqlite3.OperationalError:
            local_result_tuple = None
        if local_result_tuple:
            local_result_count = 0.0 if local_result_tuple[0] is None else local_result_tuple[0]
            with lock:
                result[disc_arg][old][dt] = local_result_count
        else:
            request_object = DISCRETE[disc_arg].request_obj(attrs=[], divs=divs, regs=regs, cities=cities, shops=shops,
                                                            old=old, beg_int=date_int, end_int=None)
            with Connect(DB) as con:
                local_result_count = con.execute(request_object.request()).fetchone()[0]
            local_result_count = 0.0 if local_result_count is None else local_result_count
            with lock:
                result[disc_arg][old][dt] = local_result_count
            insert_cache_request = cache_graph_insert(divs=divs, regs=regs, cities=cities, shops=shops, old_attr=old,
                                                      date_int=date_int, mrk_arg=disc_arg, val=local_result_count)
            while True:
                try:
                    with con_cache:
                        con_cache.execute(insert_cache_request)
                    break
                except sqlite3.OperationalError:
                    continue


def _graph_set(disc_arg: str, divs: list, regs: list, cities: list, shops: list, old: Bs.OldSign,
               dates_int_range: list, result: defaultdict):
    threads = list()
    lock = Lock()
    for date_int in dates_int_range:
        threads.append(Thread(target=_in_thread_graph_set, args=(disc_arg, divs, regs, cities, shops, old,
                                                                 dates_int_range, result, date_int, lock)))
    for thr in threads:
        thr.start()
    for thr in threads:
        thr.join()


def graph_extraction(un_args: list, disc_args: list, divs: list, regs: list, cities: list, shops: list,
                     olds: list, ones: list, dates_int_range: list) -> defaultdict:
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    result_for_one = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for old in olds:
        if un_args:
            expr_list = [UNITED[arg].calculated for arg in un_args]
            request_object = SimpleBySingle(attr=Bs.DATE_COL, expressions=expr_list, divs=divs, regs=regs,
                                            cities=cities, shops=shops, old_attr=old,
                                            date_expr=None, positive_sales=None, table=Bs.DATA_TABLE)
            with Connect(DB) as con:
                con.row_factory = sqlite3.Row
                for ln in con.execute(request_object.request()):
                    dt = date(2020, 1, 1) + timedelta(days=ln[request_object.ATTR_INDEX])
                    for arg in un_args:
                        summa = ln[arg] if ln[arg] is not None else 0.0
                        result[arg][old][dt] = summa

        for arg in disc_args:
            _graph_set(arg, divs, regs, cities, shops, old, dates_int_range, result)

        if Bs.ForOneSign.for_one.value in ones:
            shops_count = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
            _graph_set(ACTIVE_SHOPS_KEY, divs, regs, cities, shops, old, dates_int_range, shops_count)
            for dt, count in shops_count[ACTIVE_SHOPS_KEY][old].items():
                if count != 0.0:
                    for arg in un_args + disc_args:
                        summa = result[arg][old][dt]
                        setup = UNITED if arg in UNITED_KEYS else DISCRETE
                        for_one = summa if setup[arg].for_one else summa / count
                        result_for_one[arg][old][dt] = for_one
    return Result(result if Bs.ForOneSign.anyone.value in ones else None,
                  result_for_one if Bs.ForOneSign.for_one.value in ones else None)


def _table_set(disc_arg: str, divs: list, regs: list, cities: list, shops: list, old: Bs.OldSign,
               dates_int_range: list, begin: date, end: date, beg_int: int, end_int: int, period: str,
               attrs: list, connection, result: defaultdict):
    flowing, come = DISCRETE[disc_arg].flowing, DISCRETE[disc_arg].come
    if flowing and come and beg_int == dates_int_range[0]:
        dt = date(begin.year, begin.month + 1, 1) if begin.month + 1 <= 12 else date(begin.year + 1, 1, 1)
        beg_int = (dt - date(2020, 1, 1)).days
        end_int = (date(end.year, end.month, 1) - date(2020, 1, 1)).days
    elif flowing and not come and end_int == dates_int_range[-1]:
        dt = date(end.year, end.month - 1, 1) if end.month - 1 >= 1 else date(end.year - 1, 12, 1)
        end_int = (dt - date(2020, 1, 1)).days
        beg_int = (date(begin.year, begin.month, 1) - date(2020, 1, 1)).days
    else:
        beg_int = (date(begin.year, begin.month, 1) - date(2020, 1, 1)).days
        end_int = (date(end.year, end.month, 1) - date(2020, 1, 1)).days
    cache_request = cache_table_extract(divs=divs, regs=regs, cities=cities, shops=shops, old_attr=old,
                                        begin_int=beg_int, end_int=end_int, attr_columns=attrs, mark_argument=disc_arg)
    with Connect(DB_CACHE_TABLE) as con_cache:
        try:
            rows = con_cache.execute(cache_request).fetchall()
        except sqlite3.OperationalError:
            rows = None
        if rows:
            for ln in rows:
                attr_key, summa = tuple((int(i) for i in ln[0].split())), ln[1] if ln[1] is not None else 0.0
                result[attr_key][old][disc_arg][period] = summa
        else:
            request_obj = DISCRETE[disc_arg].request_obj(attrs=attrs, divs=divs, regs=regs, cities=cities,
                                                         shops=shops, old=old, beg_int=beg_int, end_int=end_int)
            rows = connection.execute(request_obj.request()).fetchall()
            inserts = list()
            for ln in rows:
                attr_key = ln[:request_obj.attrs_slice_bound] if not request_obj.is_empty_attrs else tuple()
                summa = ln[-1] if ln[-1] is not None else 0.0
                result[attr_key][old][disc_arg][period] = summa
                attr_key_string = f"{' '.join([str(i) for i in attr_key])}"
                inserts.append((attr_key_string, summa))
            insert_cache_request = cache_table_insert(divs=divs, regs=regs, cities=cities, shops=shops, old_attr=old,
                                                      begin_int=beg_int, end_int=end_int, attr_columns=attrs,
                                                      mrk_arg=disc_arg)
            try:
                with con_cache:
                    con_cache.executemany(insert_cache_request, inserts)
            except sqlite3.OperationalError:
                pass


def table_extraction(un_args: list, disc_args: list, divs: list, regs: list, cities: list, shops: list,
                     olds: list, ones: list, dates_int_range: list,
                     begin: date, end: date, attrs: list, result: defaultdict, result_for_one: defaultdict):
    beg_int, end_int = (begin - date(2020, 1, 1)).days, (end - date(2020, 1, 1)).days
    period = "-".join((begin.strftime("%m.%y"), end.strftime("%m.%y")))
    with Connect(DB) as con:
        con.row_factory = sqlite3.Row
        for old in olds:
            if un_args:
                expr_list = [UNITED[arg].calculated for arg in un_args]
                date_expr = f"{Bs.DATE_COL} >= {beg_int} and {Bs.DATE_COL} <= {end_int}"
                request_object = SimpleByMultiples(attrs=attrs, expressions=expr_list, divs=divs, regs=regs,
                                                   cities=cities, shops=shops, old_attr=old,
                                                   date_expr=date_expr, positive_sales=None, table=Bs.DATA_TABLE)
                for ln in con.execute(request_object.request()):
                    attr_key = ln[:request_object.attrs_slice_bound] if not request_object.is_empty_attrs else tuple()
                    for arg in un_args:
                        summa = ln[arg] if ln[arg] is not None else 0.0
                        result[attr_key][old][arg][period] = summa

            for arg in disc_args:
                _table_set(disc_arg=arg, divs=divs, regs=regs, cities=cities, shops=shops, old=old,
                           dates_int_range=dates_int_range, begin=begin, end=end,
                           beg_int=beg_int, end_int=end_int, period=period, attrs=attrs, connection=con,
                           result=result)

            if Bs.ForOneSign.for_one.value in ones:
                shops_qnt_obj = DISCRETE[ACTIVE_SHOPS_KEY].request_obj(attrs=attrs, divs=divs, regs=regs, cities=cities,
                                                                       shops=shops, old=old,
                                                                       beg_int=beg_int, end_int=end_int)
                for ln in con.execute(shops_qnt_obj.request()):
                    attr_key = ln[:shops_qnt_obj.attrs_slice_bound] if not shops_qnt_obj.is_empty_attrs else tuple()
                    count = ln[-1] if ln[-1] is not None else 0.0
                    if count != 0.0:
                        for arg in un_args + disc_args:
                            summa = result[attr_key][old][arg][period]
                            setup = UNITED if arg in UNITED_KEYS else DISCRETE
                            for_one = summa if setup[arg].for_one else summa / count
                            result_for_one[attr_key][old][arg][period] = for_one
