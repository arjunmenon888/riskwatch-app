import dash
from dash import dcc, html, Input, Output

# Import the feature-specific modules
import observation_app
import near_miss_app
import landing_page  # --- MODULE IS ALREADY IMPORTED ---

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
landing_page.register_callbacks(app) # <<<--- THIS WAS THE MISSING LINE. IT IS NOW ADDED.


# --- PAGE LAYOUTS ARE NOW HANDLED BY THE ROUTING CALLBACK ---


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
        # --- CALL THE LAYOUT FUNCTION FROM THE DEDICATED MODULE ---
        return landing_page.create_layout(app)


# --- Main Entry Point ---
if __name__ == '__main__':
    app.run(debug=True)