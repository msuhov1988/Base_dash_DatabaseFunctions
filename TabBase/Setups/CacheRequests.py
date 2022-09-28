import TabBase.Setups.BaseSettings as Bs


def cache_graph_extract(divs: list, regs: list, cities: list, shops: list, old_attr: Bs.OldSign,
                        date_int: int, mark_argument: str):
    divs = [str(i) for i in sorted(divs)]
    regs = [str(i) for i in sorted(regs)]
    cities = [str(i) for i in sorted(cities)]
    shops = [str(i) for i in sorted(shops)]
    where_line = [f"{Bs.DATE_COL} = {date_int}"]
    if shops:
        where_line.append(f"shops = '{' '.join(shops)}'")
    else:
        where_line.extend([f"divs = '{' '.join(divs)}'",
                           f"regs = '{' '.join(regs)}'",
                           f"cities = '{' '.join(cities)}'"])
    where_line.append(f"{Bs.OLD_SHOP_COL} = {Bs.DB_OLD_SIGN if old_attr == Bs.OldSign.old_only.value else 0}")
    where_line.append(f"mark_argument = '{mark_argument}'")
    return f"""SELECT value
               FROM graph_cache
               WHERE {' and '.join(where_line)}"""


def cache_graph_insert(divs: list, regs: list, cities: list, shops: list, old_attr: Bs.OldSign,
                       date_int: int, mrk_arg: str, val: float):
    divs = f"'{' '.join([str(i) for i in sorted(divs)])}'"
    regs = f"'{' '.join([str(i) for i in sorted(regs)])}'"
    cities = f"'{' '.join([str(i) for i in sorted(cities)])}'"
    shops = f"'{' '.join([str(i) for i in sorted(shops)])}'"
    old = Bs.DB_OLD_SIGN if old_attr == Bs.OldSign.old_only.value else 0

    return f"INSERT INTO graph_cache VALUES ({date_int},{divs},{regs},{cities},{shops},{old},'{mrk_arg}',{val})"


def cache_table_extract(divs: list, regs: list, cities: list, shops: list, old_attr: Bs.OldSign,
                        begin_int: int, end_int: int, attr_columns: list, mark_argument: str):
    divs = [str(i) for i in sorted(divs)]
    regs = [str(i) for i in sorted(regs)]
    cities = [str(i) for i in sorted(cities)]
    shops = [str(i) for i in sorted(shops)]
    where_line = [f"begin_int = {begin_int} and end_int = {end_int}", f"attr_columns = '{' '.join(attr_columns)}'"]
    if shops:
        where_line.append(f"shops = '{' '.join(shops)}'")
    else:
        where_line.extend([f"divs = '{' '.join(divs)}'",
                           f"regs = '{' '.join(regs)}'",
                           f"cities = '{' '.join(cities)}'"])
    where_line.append(f"{Bs.OLD_SHOP_COL} = {Bs.DB_OLD_SIGN if old_attr == Bs.OldSign.old_only.value else 0}")
    where_line.append(f"mark_argument = '{mark_argument}'")
    return f"""SELECT attr_values, value
               FROM table_cache
               WHERE {' and '.join(where_line)}"""


def cache_table_insert(divs: list, regs: list, cities: list, shops: list, old_attr: Bs.OldSign,
                       begin_int: int, end_int: int, attr_columns: list, mrk_arg: str):
    divs = f"'{' '.join([str(i) for i in sorted(divs)])}'"
    regs = f"'{' '.join([str(i) for i in sorted(regs)])}'"
    cities = f"'{' '.join([str(i) for i in sorted(cities)])}'"
    shops = f"'{' '.join([str(i) for i in sorted(shops)])}'"
    old = Bs.DB_OLD_SIGN if old_attr == Bs.OldSign.old_only.value else 0
    return f"""INSERT INTO table_cache VALUES ({begin_int},{end_int},'{' '.join(attr_columns)}',
                                               {divs},{regs},{cities},{shops},{old},'{mrk_arg}',?,?)"""
