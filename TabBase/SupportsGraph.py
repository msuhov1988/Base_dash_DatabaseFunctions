from .Setups import BaseSettings as Bs
from .Setups import ExtractData as Efn
from .Setups.SumObject import UNITED
from .Setups.SetObject import DISCRETE
import os.path
from os import getpid
from datetime import date
from statistics import mean
from openpyxl import Workbook
import plotly.graph_objects as go
from enum import Enum


class Section(Enum):
    basic = "ОСН-Й"
    comparative = "СРАВН"


TRACE_NAME_SEP = "  "


def _range_months(less_date: date, great_date: date):
    result = list()
    delta = (great_date.year - less_date.year) * 12 + great_date.month - less_date.month
    temp = less_date
    i = 0
    while i <= delta:
        result.append(temp)
        temp = date(temp.year, temp.month + 1, 1) if temp.month + 1 <= 12 else date(temp.year + 1, 1, 1)
        i += 1
    return result


def _graph_lines(section: Section, line_type: Bs.LineType, base_dict: dict, for_one_dict: dict, traces: list) -> list:
    for num, data in enumerate((base_dict, for_one_dict)):
        if not data:
            continue
        for_one_label = Bs.ForOneSign.for_one.value if num == 1 else ""
        for mark, old_dict in data.items():
            try:
                label, plot_type = UNITED[mark].label, UNITED[mark].plot
            except KeyError:
                label, plot_type = DISCRETE[mark].label, DISCRETE[mark].plot
            for old, date_dict in old_dict.items():
                name = TRACE_NAME_SEP.join((section, old, label, for_one_label))
                abscissa = _range_months(min(date_dict.keys()), max(date_dict.keys()))
                if line_type != Bs.LineType.years.value:
                    ordinate = list()
                    for dt in abscissa:
                        try:
                            ordinate.append(date_dict[dt])
                        except KeyError:
                            ordinate.append(0.0)
                    traces.append(plot_type(x=abscissa, y=ordinate, name=name))
                else:
                    years = list({dt.year for dt in abscissa})
                    years.sort()
                    for year in years:
                        year_abc = [dt.month for dt in abscissa if dt.year == year]
                        temp_abc = [dt for dt in abscissa if dt.year == year]
                        year_ord = list()
                        for dt in temp_abc:
                            try:
                                year_ord.append(date_dict[dt])
                            except KeyError:
                                year_ord.append(0.0)
                        traces.append(plot_type(x=year_abc, y=year_ord, name=f"{name}{TRACE_NAME_SEP}{str(year)}"))


def graph_update(divs: list, regs: list, cities: list, shops: list, compare_activate: list,
                 divs_compare: list, regs_compare: list, cities_compare: list, shops_compare: list,
                 un_args: list, disc_args: list, ones: list, olds: list, line_type: Bs.LineType, dates_int_range: list):
    traces = list()
    base, base_for = Efn.graph_extraction(un_args=un_args, disc_args=disc_args, divs=divs, regs=regs, cities=cities,
                                          shops=shops, olds=olds, ones=ones, dates_int_range=dates_int_range)
    _graph_lines(Section.basic.value, line_type, base_dict=base, for_one_dict=base_for, traces=traces)
    if compare_activate:
        cmp, cmp_for = Efn.graph_extraction(un_args=un_args, disc_args=disc_args, divs=divs_compare, regs=regs_compare,
                                            cities=cities_compare, shops=shops_compare, olds=olds, ones=ones,
                                            dates_int_range=dates_int_range)
        _graph_lines(Section.comparative.value, line_type, base_dict=cmp, for_one_dict=cmp_for, traces=traces)

    layout_dict = dict()
    if traces:
        traces.sort(key=lambda trc: mean(trc.y))
        ind = 1
        traces[0].yaxis = "y" + str(ind)
        base_mean = mean(traces[0].y)
        for i in range(1, len(traces)):
            current_mean = mean(traces[i].y)
            if base_mean <= 1.0 and current_mean <= 1.0:
                traces[i].yaxis = "y" + str(ind)
            elif current_mean <= base_mean * 5:
                traces[i].yaxis = "y" + str(ind)
            else:
                ind += 1
                traces[i].yaxis = "y" + str(ind)
                base_mean = current_mean
        traces.sort(key=lambda trc: trc.name)
        for trace in traces:
            trace.y = [None if val == 0.0 else val for val in trace.y]
        for j in range(1, ind + 1):
            if j == 1:
                layout_dict["yaxis"] = dict()
            elif j % 2 == 1:
                layout_dict["yaxis" + str(j)] = dict(overlaying='y', side='left', anchor='free', position=0.05,
                                                     gridcolor="#212529")
            else:
                layout_dict["yaxis" + str(j)] = dict(overlaying='y', side='right', anchor='free', position=0.95,
                                                     gridcolor="#212529")

    figure = go.Figure(data=traces, layout=go.Layout(**layout_dict))
    figure.update_layout(
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        yaxis={"gridcolor": "#212529"},
        xaxis={"gridcolor": "#212529"},
        legend={"font": {"color": "#fff"}})
    return figure


def graph_download(divs: list, regs: list, cities: list, shops: list, compare_activate: list,
                   divs_comp: list, regs_comp: list, cities_comp: list, shops_comp: list,
                   un_args: list, disc_args: list, ones: list, olds: list, line_type: Bs.LineType,
                   dates_int_range: list, names_comparison: dict):
    dv = " ".join([names_comparison[Bs.DIV_ID_COL][num] for num in divs]) if divs else 'ИТОГО'
    rg = " ".join([names_comparison[Bs.REG_ID_COL][num] for num in regs]) if regs else 'ИТОГО'
    ct = " ".join([names_comparison[Bs.CITY_ID_COL][num] for num in cities]) if cities else 'ИТОГО'
    sh = " ".join([names_comparison[Bs.SHOP_ID_COL][num] for num in shops]) if shops else 'ИТОГО'

    dv_comp = " ".join([names_comparison[Bs.DIV_ID_COL][num] for num in divs_comp]) if divs_comp else 'ИТОГО'
    rg_comp = " ".join([names_comparison[Bs.REG_ID_COL][num] for num in regs_comp]) if regs_comp else 'ИТОГО'
    ct_comp = " ".join([names_comparison[Bs.CITY_ID_COL][num] for num in cities_comp]) if cities_comp else 'ИТОГО'
    sh_comp = " ".join([names_comparison[Bs.SHOP_ID_COL][num] for num in shops_comp]) if shops_comp else 'ИТОГО'

    traces = list()
    base, base_for = Efn.graph_extraction(un_args=un_args, disc_args=disc_args, divs=divs, regs=regs, cities=cities,
                                          shops=shops, olds=olds, ones=ones, dates_int_range=dates_int_range)
    _graph_lines(Section.basic.value, line_type, base_dict=base, for_one_dict=base_for, traces=traces)
    if compare_activate:
        cmp, cmp_for = Efn.graph_extraction(un_args=un_args, disc_args=disc_args, divs=divs_comp, regs=regs_comp,
                                            cities=cities_comp, shops=shops_comp, olds=olds, ones=ones,
                                            dates_int_range=dates_int_range)
        _graph_lines(Section.comparative.value, line_type, base_dict=cmp, for_one_dict=cmp_for, traces=traces)

    wb = Workbook()
    ws = wb.active
    title = ["Дивизион", "Регион", "Нас. пункт", "Магазин", "Срез", "ДТТ", "Тип данных", "ВСЕ / НА_ТТ"]
    if line_type == Bs.LineType.years.value:
        title.append("Год")
        title.extend(range(1, 13))
        ws.append(title)
        for trace in traces:
            line = [dv, rg, ct, sh] if Section.basic.value in trace.name else [dv_comp, rg_comp, ct_comp, sh_comp]
            line.extend(trace.name.split(TRACE_NAME_SEP))
            data = [None] * 12
            for i, month in enumerate(trace.x):
                if trace.y[i]:
                    data[month - 1] = trace.y[i]
            line.extend(data)
            ws.append(line)
    else:
        dates = list({dt for trace in traces for dt in trace.x})
        dates.sort()
        period, first = len(dates), min(dates)
        title.extend(dates)
        ws.append(title)
        for trace in traces:
            line = [dv, rg, ct, sh] if Section.basic.value in trace.name else [dv_comp, rg_comp, ct_comp, sh_comp]
            line.extend(trace.name.split(TRACE_NAME_SEP))
            data = [None] * period
            for i, dt in enumerate(trace.x):
                ind = (dt.year - first.year) * 12 + dt.month - first.month
                if trace.y[i]:
                    data[ind] = trace.y[i]
            line.extend(data)
            ws.append(line)

    base_folder = os.path.split(os.path.dirname(__file__))[0]
    file_name = f"_file_exports\\graph_data_{getpid()}.xlsx"
    out_file = os.path.join(base_folder, file_name)
    wb.save(out_file)
    wb.close()
    return out_file
