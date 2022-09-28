import DbModules.RandomCreation as Db
import TabBase.Setups.BaseSettings as Bs
from TabBase import BaseLayout, BaseCallbacks
from datetime import date, timedelta
from dash import Dash
from dash import dcc
import dash_bootstrap_components as dbc
from fastapi import FastAPI
import uvicorn
from starlette.middleware.wsgi import WSGIMiddleware


if __name__ == "__main__":
    Db.creation()
DATE_INT_RANGE = Bs.dates_of_database()
BEGIN_DATE = (date(2020, 1, 1) + timedelta(days=DATE_INT_RANGE[0]))
END_DATE = (date(2020, 1, 1) + timedelta(days=DATE_INT_RANGE[-1]))
REFERS, DROP_DIV, DROP_REG, DROP_CITY, DROP_SHOP, NAMES_COMPARISON = Bs.references()

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.layout =\
    dcc.Tabs([
        dcc.Tab(label="Базовая", children=[BaseLayout.layout_create(DROP_DIV, DROP_REG, DROP_CITY, DROP_SHOP,
                                                                    END_DATE, BEGIN_DATE)])
    ])
BaseCallbacks.base_register_callbacks(app, REFERS, DROP_DIV, DROP_REG, DROP_CITY, DROP_SHOP, DATE_INT_RANGE,
                                      NAMES_COMPARISON)
server = FastAPI()
server.mount("", WSGIMiddleware(app.server))

if __name__ == "__main__":
    uvicorn.run("DashApp:server", host="0.0.0.0", port=8050, workers=12)
    # app.run_server(host="127.0.0.1", debug=True)
