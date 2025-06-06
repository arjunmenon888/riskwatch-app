import dash
from dash import dcc, html, Input, Output

# Import the feature-specific modules
import observation_app
import near_miss_app

# Import and initialize the database
import database
database.init_db()


# --- Dash App Initialization ---
# This is the single Dash app instance for the entire project.
app = dash.Dash(__name__, title="RiskWatch", update_title=None, suppress_callback_exceptions=True)
server = app.server


# --- Main App Layout ---
# This is the core layout. The content of 'page-content' is rendered by the display_page callback.
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# --- Register Callbacks from Modules ---
# This crucial step connects the callbacks defined in your feature modules to the main app.
observation_app.register_callbacks(app)
near_miss_app.register_callbacks(app)


# --- Page Layouts (Core App) ---
def build_home_page():
    """Builds the layout for the home/navigation page."""
    return html.Div(className="home-container", children=[
        html.Img(src=app.get_asset_url('25h Logos.png'), alt="RiskWatch Logo", className="app-logo"),
        html.Div(className="home-button-container", children=[
            dcc.Link("Safety Observation", href="/observation", className="button-style"),
            dcc.Link("Near Miss Report", href="/near-miss", className="button-style")
        ])
    ])


# --- Main Routing Callback ---
# This callback reads the URL and returns the correct page layout from the appropriate module.
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/observation':
        return observation_app.build_observation_form_page()
    elif pathname == '/report':
        return observation_app.build_report_page()
    elif pathname == '/near-miss':
        return near_miss_app.build_near_miss_page()
    else:
        return build_home_page()


# --- Main Entry Point ---
if __name__ == '__main__':
    app.run(debug=True)