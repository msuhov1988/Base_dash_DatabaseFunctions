from .Setups import BaseSettings as Bs
from .Setups import ExtractData as Efn
from .Setups.SumObject import UNITED
from .Setups.SetObject import DISCRETE
import os.path
from os import getpid
from datetime import date, datetime
from collections import defaultdict, namedtuple
from openpyxl import Workbook
from dash import dash_table
from dash.dash_table import FormatTemplate
from dash.dash_table.Format import Format


def _table_columns(period, period_compare, table_slice: list, ones: list, olds: list,
                   un_args: list, disc_args: list):
    columns = [dict(name=Bs.TABLE_SLICES[slc], id=slc) for slc in table_slice]
    if Bs.OldSign.old_only.value in olds:
        columns.append(dict(name=Bs.OldSign.old_only.value, id=Bs.OldSign.old_only.value))
    if Bs.ForOneSign.for_one.value in ones:
        columns.append(dict(name=Bs.ForOneSign.for_one.value, id=Bs.ForOneSign.for_one.value))
    percentage = FormatTemplate.percentage(2)
    for arg in un_args + disc_args:
        try:
            label, percent = UNITED[arg].label, UNITED[arg].percent
        except KeyError:
            label, percent = DISCRETE[arg].label, DISCRETE[arg].percent
        for per in (period_compare, period):
            if not per:
                continue
            col_id = " ".join((label.upper(), per))
            if percent:
                columns.append(dict(name=col_id, id=col_id, type='numeric', format=percentage))
            else:
                columns.append(dict(name=col_id, id=col_id, type='numeric',
                                    format=Format().group(True).group_delimiter(" ")))
        if period_compare and period:
            col_id = " ".join((label.upper(), "РОСТ %"))
            columns.append(dict(name=col_id, id=col_id, type='numeric', format=percentage))
    return columns


def _table_rows(table_slice: list, base_dict: dict, for_one_dict: dict, names_comparison: dict, rows: list):
    for num, data in enumerate((base_dict, for_one_dict)):
        if not data:
            continue
        for_one_label = Bs.ForOneSign.for_one.value if num == 1 else ''
        for attr_key, old_dict in data.items():
            for old, mark_dict in old_dict.items():
                row = {key: names_comparison[key][attr_key[num]] for num, key in enumerate(table_slice)}
                row[Bs.ForOneSign.for_one.value] = for_one_label
                row[Bs.OldSign.old_only.value] = old
                for mark, period_dict in mark_dict.items():
                    try:
                        label, percent = UNITED[mark].label, UNITED[mark].percent
                    except KeyError:
                        label, percent = DISCRETE[mark].label, DISCRETE[mark].percent
                    for period, val in period_dict.items():
                        if percent:
                            row_value = round(val, 4)
                        elif val < 100:
                            row_value = round(val, 1)
                        else:
                            row_value = round(val, 0)
                        row[" ".join((label.upper(), period))] = row_value
                rows.append(row)


def table_update(begin: str, end: str, begin_compare: str, end_compare: str,
                 divs: list, regs: list, cities: list, shops: list,
                 table_slice: list, ones: list, olds: list, un_args: list, disc_args: list,
                 dates_int_range: list, names_comparison: dict, file=False):
    begin_date = datetime.strptime(begin, "%Y-%m-%d").date() if begin is not None else None
    end_date = datetime.strptime(end, "%Y-%m-%d").date() if end is not None else None
    period = "-".join((begin_date.strftime("%m.%y"), end_date.strftime("%m.%y"))) if all((begin, end)) else None
    begin_compare_date = datetime.strptime(begin_compare, "%Y-%m-%d").date() if begin_compare is not None else None
    end_compare_date = datetime.strptime(end_compare, "%Y-%m-%d").date() if end_compare is not None else None
    if all((begin_compare, end_compare)):
        period_compare = "-".join((begin_compare_date.strftime("%m.%y"), end_compare_date.strftime("%m.%y")))
    else:
        period_compare = None

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))
    data_for_one = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(float))))
    for num, per in enumerate((period, period_compare)):
        if per:
            beg, en = (begin_date, end_date) if num == 0 else (begin_compare_date, end_compare_date)
            Efn.table_extraction(un_args=un_args, disc_args=disc_args, divs=divs, regs=regs, cities=cities, shops=shops,
                                 olds=olds, ones=ones, dates_int_range=dates_int_range,
                                 begin=beg, end=en, attrs=table_slice, result=data, result_for_one=data_for_one)
    data = data if Bs.ForOneSign.anyone.value in ones else None
    data_for_one = data_for_one if Bs.ForOneSign.for_one.value in ones else None

    columns = _table_columns(period=period, period_compare=period_compare, table_slice=table_slice,
                             ones=ones, olds=olds, un_args=un_args, disc_args=disc_args)
    rows = list()
    _table_rows(table_slice=table_slice, base_dict=data, for_one_dict=data_for_one,
                names_comparison=names_comparison, rows=rows)

    for i in range(len(table_slice) - 1, -1, -1):
        rows.sort(key=lambda rw: rw[table_slice[i]])
    if period and period_compare:
        for arg in un_args + disc_args:
            label = UNITED[arg].label if arg in Efn.UNITED_KEYS else DISCRETE[arg].label
            percent = UNITED[arg].percent if arg in Efn.UNITED_KEYS else DISCRETE[arg].percent
            grow_col = " ".join((label.upper(), "РОСТ %"))
            col = " ".join((label.upper(), period))
            cmp_col = " ".join((label.upper(), period_compare))
            for row in rows:
                try:
                    try:
                        row[grow_col] = row[col] - row[cmp_col] if percent else row[col] / row[cmp_col] - 1
                    except ZeroDivisionError:
                        row[grow_col] = None
                except KeyError as err:
                    row[err.args[0]] = 0.0
                    row[grow_col] = None

    if file:
        wb = Workbook()
        ws = wb.active
        ws.append([col["name"] for col in columns])
        temp = [col["id"] for col in columns]
        for row in rows:
            line = []
            for ind in temp:
                try:
                    line.append(row[ind])
                except KeyError:
                    line.append(None)
            ws.append(line)
        base_folder = os.path.split(os.path.dirname(__file__))[0]
        file_name = f"_file_exports\\table_data_{getpid()}.xlsx"
        out_file = os.path.join(base_folder, file_name)
        wb.save(out_file)
        wb.close()
        return out_file

    cell_condition = ([{'if': {'column_id': "real_end"},
                        'border-right': '5px double black'}])
    cell_condition.extend([{'if': {'column_id': c['id']},
                            'border-right': '5px double black'} for c in columns if "РОСТ" in c['id']])
    data_condition = [{
                       "if": {'filter_query': "{{{0}}} >= 0.1".format(c['id']),
                              'column_id': c['id']},
                       'color': '#77b300'
                       } for c in columns if "РОСТ" in c['id']]
    data_condition.extend([{
                            "if": {'filter_query': "{{{0}}} >= 0.0 and {{{0}}} < 0.1".format(c['id']),
                                   'column_id': c['id']},
                            'color': '#f80'
                            } for c in columns if "РОСТ" in c['id']])
    data_condition.extend([{
                            "if": {'filter_query': "{{{0}}} < 0.0".format(c['id']),
                                   'column_id': c['id']},
                            'color': '#c00'
                            } for c in columns if "РОСТ" in c['id']])

    return dash_table.DataTable(
        style_header={'whiteSpace': 'normal', 'height': 'auto',
                      'backgroundColor': '#222', 'color': 'white',
                      'border-bottom': '5px double black', 'fontWeight': 'bold'},
        style_cell={'backgroundColor': '#222', "color": "#adafae", 'fontWeight': 'bold', 'border': '2px double black'},
        cell_selectable=False,
        columns=columns,
        data=rows,
        page_size=24,
        style_table={'overflowX': 'auto'},
        sort_action="native",
        sort_mode="multi",
        style_header_conditional=cell_condition,
        style_cell_conditional=cell_condition,
        style_data_conditional=data_condition)
