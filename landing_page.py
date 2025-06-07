# landing_page.py

from dash import dcc, html, Input, Output, State, callback_context

def create_layout(app_instance):
    """
    Creates the layout for the full-width, responsive landing page.
    """
    return html.Div(className="landing-page-wrapper", children=[
        # Header/Navbar Section
        html.Header(className="landing-header", children=[
            html.Img(
                src=app_instance.get_asset_url('riskwatch-logo.png'),
                alt="Risk Watch Logo",
                className="landing-logo-img"
            ),
            html.Nav(className="landing-navbar", children=[
                # Sandwich button for mobile
                html.Button(className="mobile-menu-toggle", id="mobile-menu-toggle", children=[
                    html.Span(className="toggle-bar"),
                    html.Span(className="toggle-bar"),
                    html.Span(className="toggle-bar"),
                ]),
                # Main navigation links
                html.Ul(className="nav-links", id="nav-links-ul", children=[
                    html.Li(className="nav-item dropdown", children=[
                        html.A("Services", href="#", className="nav-link-item", id="services-dropdown-toggle"),
                        html.Ul(className="dropdown-content", id="services-dropdown-content", children=[
                            html.Li(dcc.Link("Safety Observation Report", href="/observation", className="dropdown-link-item"))
                        ])
                    ]),
                    html.Li(html.A("About", href="#", className="nav-link-item")),
                    html.Li(html.A("Contact Us", href="#", className="nav-link-item")),
                    html.Li(html.A("Register", href="#", className="nav-link-item")),
                    html.Li(html.A("Log In", href="#", className="nav-link-item")),
                ])
            ])
        ]),

        # Hero Section
        html.Main(className="hero-section", children=[
            html.Div(className="hero-left", children=[
                html.H1([
                    html.Span("Risk Watch", style={'fontWeight': 'bold'}),
                    " is an AI-powered assistant built for HSE professionals. We help you capture observations, assess risks, and generate compliance-ready reports instantly."
                ], className="hero-headline")
            ]),
            html.Div(className="hero-right", children=[
                html.P(
                    "Trusted by safety managers, ISO-aligned teams, and forward-thinking HSE innovators.",
                    className="hero-trust-text"
                )
            ])
        ])
    ])


def register_callbacks(app):
    """Registers callbacks for the landing page."""

    # Callback for the desktop dropdown
    @app.callback(
        Output('services-dropdown-content', 'style'),
        Input('services-dropdown-toggle', 'n_clicks'),
        State('services-dropdown-content', 'style'),
        prevent_initial_call=True
    )
    def toggle_services_dropdown(n_clicks, current_style):
        if current_style and current_style.get('display') == 'block':
            return {'display': 'none'}
        else:
            return {'display': 'block'}

    # Callback for the mobile menu (sandwich button)
    @app.callback(
        Output('nav-links-ul', 'className'),
        Input('mobile-menu-toggle', 'n_clicks'),
        State('nav-links-ul', 'className'),
        prevent_initial_call=True
    )
    def toggle_mobile_menu(n_clicks, current_class):
        if 'active' in current_class:
            return "nav-links"
        else:
            return "nav-links active"