import TabBase.Setups.BaseSettings as Bs


def _where_builder(divs: list, regs: list, cities: list, shops: list,
                   old_attr: Bs.OldSign, date_expr=None, positive_sales=None) -> tuple:
    shop_whr = city_whr = reg_whr = div_whr = ""
    if shops:
        shop_whr = f"{Bs.SHOP_ID_COL} = {shops[0]}" if len(shops) == 1 else f"{Bs.SHOP_ID_COL} in {tuple(shops)}"
    else:
        if cities:
            city_whr = f"{Bs.CITY_ID_COL} = {cities[0]}" if len(cities) == 1 else f"{Bs.CITY_ID_COL} in {tuple(cities)}"
        if regs:
            reg_whr = f"{Bs.REG_ID_COL} = {regs[0]}" if len(regs) == 1 else f"{Bs.REG_ID_COL} in {tuple(regs)}"
        if divs:
            div_whr = f"{Bs.DIV_ID_COL} = {divs[0]}" if len(divs) == 1 else f"{Bs.DIV_ID_COL} in {tuple(divs)}"
    old_whr = f"{Bs.OLD_SHOP_COL} = {Bs.DB_OLD_SIGN}" if old_attr == Bs.OldSign.old_only.value else ""
    return tuple((e for e in (date_expr, shop_whr, city_whr, reg_whr, div_whr, old_whr, positive_sales) if e))


class SimpleBySingle:

    ATTR_INDEX = 0

    def __init__(self, attr: str, expressions: list, divs: list, regs: list, cities: list, shops: list,
                 old_attr: Bs.OldSign, date_expr=None, positive_sales=None, table=Bs.DATA_TABLE):
        assert bool(attr), print('Argument "attr" in SimpleBySingle must be a nonempty string')
        self.select = (attr, *expressions)
        self.from_table = table
        self.where = _where_builder(divs, regs, cities, shops, old_attr, date_expr, positive_sales)
        self.group = attr

    def request(self):
        select_str = f"SELECT {', '.join(self.select)}"
        from_str = f"FROM {self.from_table}"
        where_str = f"WHERE {' and '.join(self.where)}" if self.where else ""
        group_str = f"GROUP BY {self.group}"
        return f"{select_str}\n{from_str}\n{where_str}\n{group_str}"


class SimpleByMultiples:

    # for random length of attrs, including zero length
    def __init__(self, attrs: list, expressions: list, divs: list, regs: list, cities: list, shops: list,
                 old_attr: Bs.OldSign, date_expr=None, positive_sales=None, table=Bs.DATA_TABLE):
        self.select = tuple((e for e in (*attrs, *expressions) if e))
        self.from_table = table
        self.where = _where_builder(divs, regs, cities, shops, old_attr, date_expr, positive_sales)
        self.group = tuple((e for e in attrs if e))
        self.attrs_slice_bound = len(attrs) if attrs else None
        self.is_empty_attrs = False if attrs else True

    def request(self):
        select_str = f"SELECT {', '.join(self.select)}"
        from_str = f"FROM {self.from_table}"
        where_str = f"WHERE {' and '.join(self.where)}" if self.where else ""
        group_str = f"GROUP BY {', '.join(self.group)}" if self.group else ""
        return f"{select_str}\n{from_str}\n{where_str}\n{group_str}"


def set_except_request(attrs: list, outer_expr: str, upper_inner_expr: str, lower_inner_expr: str,
                       divs: list, regs: list, cities: list, shops: list, old_attr: Bs.OldSign, positive_sales: str,
                       date_expr_one: str, date_expr_two: str, upper_table: str, lower_table: str):
    upper_inner = SimpleByMultiples(attrs, [upper_inner_expr], divs, regs, cities, shops, old_attr,
                                    date_expr_one, positive_sales, upper_table)
    lower_inner = SimpleByMultiples(attrs, [lower_inner_expr], divs, regs, cities, shops, old_attr,
                                    date_expr_two, positive_sales, lower_table)
    upper_inner.group = lower_inner.group = ""
    outer_table = f"({upper_inner.request()}\nEXCEPT\n{lower_inner.request()})"
    result_obj = SimpleByMultiples(attrs=attrs, expressions=[outer_expr], divs=[], regs=[], cities=[], shops=[],
                                   old_attr='', table=outer_table)
    return result_obj


def joined_request(attrs: list, upper_inner_expr: str, lower_inner_expr: str,
                   divs: list, regs: list, cities: list, shops: list, old_attr: Bs.OldSign,
                   date_expr: str, upper_table: str, lower_table: str):
    upper_inner_expr += ' as upper'
    lower_inner_expr += ' as lower'
    upper_inner_request = SimpleByMultiples(attrs, [upper_inner_expr], divs, regs, cities, shops, old_attr,
                                            date_expr, table=upper_table).request()
    lower_inner_request = SimpleByMultiples(attrs, [lower_inner_expr], divs, regs, cities, shops, old_attr,
                                            date_expr, table=lower_table).request()
    outer_attrs = [f"R1.{e}" for e in attrs]
    join_cond = [f"R1.{e} = R2.{e}" for e in attrs]
    join_cond = f"ON {' and '.join(join_cond)}" if join_cond else ""
    outer_table = f"({upper_inner_request}) as R1\nINNER JOIN\n({lower_inner_request}) as R2\n{join_cond}"
    req = SimpleByMultiples(attrs=outer_attrs, expressions=['R1.upper / R2.lower'],
                            divs=[], regs=[], cities=[], shops=[],
                            old_attr='', table=outer_table)
    req.group = ""
    return req
