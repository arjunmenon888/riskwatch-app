from dash import dcc, html

# --- Layout Function for Near Miss ---

def build_near_miss_page():
    """Builds the layout for the 'Under Construction' near-miss page."""
    return html.Div(className="report-container", children=[
       html.Div(className="header", children=[
           # Note: We use root-relative paths for assets in modular apps
           html.Img(src='/assets/riskwatch-logo.png', alt="RiskWatch Logo", className="app-logo"),
           html.H1("Near Miss Reporting"),
           dcc.Link('Back to Home', href='/', className='nav-link')
       ]),
       html.P("This page is under construction. Please check back later.", style={'textAlign': 'center', 'padding': '50px'})
   ])

# --- Callback Registration Function ---
def register_callbacks(app):
    """Registers callbacks for the near-miss app. Currently none."""
    # When you add forms or interactivity to the near-miss page,
    # you will register their callbacks here, just like in observation_app.py.
    pass