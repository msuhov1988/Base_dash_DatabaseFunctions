from . import SupportsGraph as Sgr
from . import SupportsTable as Stb
from dash import dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


def base_register_callbacks(app, glob_refers, glob_drop_div, glob_drop_reg, glob_drop_city, glob_drop_shops,
                            glob_dates_int_range, glob_names_comparison):
    @app.callback(
        Output("base_sales_graph", "figure"),
        Output("base_button_graph", "n_clicks"),
        Output("base_graph_loading_output", "children"),
        Input("base_divisions", "value"),
        Input("base_regions", "value"),
        Input("base_cities", "value"),
        Input("base_shops", "value"),
        Input("compare_activate", "value"),
        Input("base_divisions_compare", "value"),
        Input("base_regions_compare", "value"),
        Input("base_cities_compare", "value"),
        Input("base_shops_compare", "value"),
        Input("base_sales_checklist", "value"),
        Input("base_carts_checklist", "value"),
        Input("base_one_checklist", "value"),
        Input("base_dtt_checklist", "value"),
        Input("base_graph_radio", "value"))
    def base_graph_update(divs, regs, cities, shops, comp_activate,
                          divs_compare, regs_compare, cities_compare, shops_compare,
                          united_args, discrete_args, ones, olds, line_type):
        figure = Sgr.graph_update(divs=divs, regs=regs, cities=cities, shops=shops, compare_activate=comp_activate,
                                  divs_compare=divs_compare, regs_compare=regs_compare, cities_compare=cities_compare,
                                  shops_compare=shops_compare, un_args=united_args, disc_args=discrete_args, ones=ones,
                                  olds=olds, line_type=line_type, dates_int_range=glob_dates_int_range)
        return figure, None, []

    @app.callback(
        Output('base_graph_download', "data"),
        Output("base_graph_loading_output_file", "children"),
        Input("base_divisions", "value"),
        Input("base_regions", "value"),
        Input("base_cities", "value"),
        Input("base_shops", "value"),
        Input("compare_activate", "value"),
        Input("base_divisions_compare", "value"),
        Input("base_regions_compare", "value"),
        Input("base_cities_compare", "value"),
        Input("base_shops_compare", "value"),
        Input("base_sales_checklist", "value"),
        Input("base_carts_checklist", "value"),
        Input("base_one_checklist", "value"),
        Input("base_dtt_checklist", "value"),
        Input("base_graph_radio", "value"),
        Input("base_button_graph", "n_clicks"))
    def base_graph_download(divs, regs, cities, shops, comp_activate,
                            divs_compare, regs_compare, cities_compare, shops_compare,
                            united_args, discrete_args, ones, olds, line_type, n_clicks):
        if n_clicks is not None:
            file = Sgr.graph_download(divs=divs, regs=regs, cities=cities, shops=shops, compare_activate=comp_activate,
                                      divs_comp=divs_compare, regs_comp=regs_compare, cities_comp=cities_compare,
                                      shops_comp=shops_compare, un_args=united_args, disc_args=discrete_args, ones=ones,
                                      olds=olds, line_type=line_type, dates_int_range=glob_dates_int_range,
                                      names_comparison=glob_names_comparison)
        else:
            raise PreventUpdate

        return dcc.send_file(file), []

    @app.callback(
        Output('base_table', "children"),
        Output('base_button_table', 'n_clicks'),
        Output('base_table_loading_output', 'children'),
        Input("base_date_range", "start_date"),
        Input("base_date_range", "end_date"),
        Input("base_date_range_compare", "start_date"),
        Input("base_date_range_compare", "end_date"),
        Input("base_table_divisions", "value"),
        Input("base_table_regions", "value"),
        Input("base_table_cities", "value"),
        Input("base_table_shops", "value"),
        Input("base_table_slice_checklist", "value"),
        Input("base_table_one_checklist", "value"),
        Input("base_table_dtt_checklist", "value"),
        Input("base_table_sales_references", "value"),
        Input("base_table_carts_references", "value"))
    def base_table_update(begin, end, begin_compare, end_compare, divs, regs, cities, shops,
                          table_slices, ones, olds, united_args, discrete_args):

        return Stb.table_update(begin=begin, end=end, begin_compare=begin_compare, end_compare=end_compare,
                                divs=divs, regs=regs, cities=cities, shops=shops,
                                table_slice=table_slices, ones=ones, olds=olds,
                                un_args=united_args, disc_args=discrete_args, dates_int_range=glob_dates_int_range,
                                names_comparison=glob_names_comparison, file=False), None, []

    @app.callback(
        Output('base_table_download', "data"),
        Output('base_table_file_loading_output', 'children'),
        Input("base_date_range", "start_date"),
        Input("base_date_range", "end_date"),
        Input("base_date_range_compare", "start_date"),
        Input("base_date_range_compare", "end_date"),
        Input("base_table_divisions", "value"),
        Input("base_table_regions", "value"),
        Input("base_table_cities", "value"),
        Input("base_table_shops", "value"),
        Input("base_table_slice_checklist", "value"),
        Input("base_table_one_checklist", "value"),
        Input("base_table_dtt_checklist", "value"),
        Input("base_table_sales_references", "value"),
        Input("base_table_carts_references", "value"),
        Input('base_button_table', 'n_clicks'))
    def base_table_download(begin, end, begin_compare, end_compare, divs, regs, cities, shops,
                            table_slices, ones, olds, united_args, discrete_args, n_clicks):
        if n_clicks is not None:
            file = Stb.table_update(begin=begin, end=end, begin_compare=begin_compare, end_compare=end_compare,
                                    divs=divs, regs=regs, cities=cities, shops=shops,
                                    table_slice=table_slices, ones=ones, olds=olds,
                                    un_args=united_args, disc_args=discrete_args, dates_int_range=glob_dates_int_range,
                                    names_comparison=glob_names_comparison, file=True)
        else:
            raise PreventUpdate
        return dcc.send_file(file), []

    @app.callback(
        Output("base_regions", "options"),
        Output("base_regions", "value"),
        Input("base_divisions", "value"))
    def base_div_input(ad):
        div = ad if ad else glob_drop_div.keys()
        temp = list({i.region for i in glob_refers if i.division in div})
        temp.sort()
        return [{"label": glob_drop_reg[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_cities", "options"),
        Output("base_cities", "value"),
        Input("base_divisions", "value"),
        Input("base_regions", "value"))
    def base_div_region_input(ad, ar):
        div, reg = ad if ad else glob_drop_div.keys(), ar if ar else glob_drop_reg.keys()
        temp = list({i.city for i in glob_refers if i.division in div and i.region in reg})
        temp.sort()
        return [{"label": glob_drop_city[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_shops", "options"),
        Output("base_shops", "value"),
        Input("base_divisions", "value"),
        Input("base_regions", "value"),
        Input("base_cities", "value"))
    def base_div_region_city_input(ad, ar, ac):
        div, reg = ad if ad else glob_drop_div.keys(), ar if ar else glob_drop_reg.keys()
        city = ac if ac else glob_drop_city.keys()
        temp = list({i.shop for i in glob_refers if i.division in div and i.region in reg and i.city in city})
        temp.sort()
        return [{"label": glob_drop_shops[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_divisions_compare", "disabled"),
        Output("base_regions_compare", "disabled"),
        Output("base_cities_compare", "disabled"),
        Output("base_shops_compare", "disabled"),
        Input("compare_activate", "value"))
    def compare_activate(val):
        if val:
            return False, False, False, False
        else:
            return True, True, True, True

    @app.callback(
        Output("base_regions_compare", "options"),
        Output("base_regions_compare", "value"),
        Input("base_divisions_compare", "value"))
    def base_compare_div_input(ad):
        div = ad if ad else glob_drop_div.keys()
        temp = list({i.region for i in glob_refers if i.division in div})
        temp.sort()
        return [{"label": glob_drop_reg[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_cities_compare", "options"),
        Output("base_cities_compare", "value"),
        Input("base_divisions_compare", "value"),
        Input("base_regions_compare", "value"))
    def base_compare_div_region_input(ad, ar):
        div, reg = ad if ad else glob_drop_div.keys(), ar if ar else glob_drop_reg.keys()
        temp = list({i.city for i in glob_refers if i.division in div and i.region in reg})
        temp.sort()
        return [{"label": glob_drop_city[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_shops_compare", "options"),
        Output("base_shops_compare", "value"),
        Input("base_divisions_compare", "value"),
        Input("base_regions_compare", "value"),
        Input("base_cities_compare", "value"))
    def base_compare_div_region_city_input(ad, ar, ac):
        div, reg = ad if ad else glob_drop_div.keys(), ar if ar else glob_drop_reg.keys()
        city = ac if ac else glob_drop_city.keys()
        temp = list({i.shop for i in glob_refers if i.division in div and i.region in reg and i.city in city})
        temp.sort()
        return [{"label": glob_drop_shops[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_date_range_compare", "disabled"),
        Output("base_date_range_compare", "start_date"),
        Output("base_date_range_compare", "end_date"),
        Input("table_compare_activate", "value"))
    def table_compare_activate(val):
        if val:
            return False, None, None
        else:
            return True, None, None

    @app.callback(
        Output("base_table_regions", "options"),
        Output("base_table_regions", "value"),
        Input("base_table_divisions", "value"))
    def base_table_div_input(ad):
        div = ad if ad else glob_drop_div.keys()
        temp = list({i.region for i in glob_refers if i.division in div})
        temp.sort()
        return [{"label": glob_drop_reg[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_table_cities", "options"),
        Output("base_table_cities", "value"),
        Input("base_table_divisions", "value"),
        Input("base_table_regions", "value"))
    def base_table_div_region_input(ad, ar):
        div, reg = ad if ad else glob_drop_div.keys(), ar if ar else glob_drop_reg.keys()
        temp = list({i.city for i in glob_refers if i.division in div and i.region in reg})
        temp.sort()
        return [{"label": glob_drop_city[i], "value": i} for i in temp], []

    @app.callback(
        Output("base_table_shops", "options"),
        Output("base_table_shops", "value"),
        Input("base_table_divisions", "value"),
        Input("base_table_regions", "value"),
        Input("base_table_cities", "value"))
    def base_table_div_region_city_input(ad, ar, ac):
        div, reg = ad if ad else glob_drop_div.keys(), ar if ar else glob_drop_reg.keys()
        city = ac if ac else glob_drop_city.keys()
        temp = list({i.shop for i in glob_refers if i.division in div and i.region in reg and i.city in city})
        temp.sort()
        return [{"label": glob_drop_shops[i], "value": i} for i in temp], []
