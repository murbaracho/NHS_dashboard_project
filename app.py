import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Load the datasets
appointments = pd.read_csv("appointments_regional.csv")
appointments['appointment_month'] = pd.to_datetime(appointments['appointment_month'])

# KPIs
total_appointments = appointments['count_of_appointments'].sum()
total_months = appointments['appointment_month'].dt.to_period('M').nunique()
avg_per_month = round(total_appointments / total_months)

# Prepare data for dropdown and plots
appointment_modes = appointments['appointment_mode'].unique()
appointments_by_mode = appointments.groupby(['appointment_month', 'appointment_mode'])['count_of_appointments'].sum().reset_index()

# Add Season Column
appointments['Season'] = appointments['appointment_month'].dt.month % 12 // 3 + 1
season_map = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Autumn'}
appointments['Season'] = appointments['Season'].map(season_map)

appointments_by_season = appointments.groupby(['Season'])['count_of_appointments'].sum().reset_index()

# App setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.title = "NHS Dashboard"

app.layout = dbc.Container([
    html.H1("NHS Appointments Dashboard", className='my-4 text-center'),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Appointments"),
            dbc.CardBody(html.H4(f"{total_appointments:,}"))
        ]), md=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total Months"),
            dbc.CardBody(html.H4(f"{total_months}"))
        ]), md=4),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Avg per Month"),
            dbc.CardBody(html.H4(f"{avg_per_month:,}"))
        ]), md=4),
    ], className="mb-4"),

    html.Label("Select Appointment Mode:"),
    dcc.Dropdown(
        options=[{"label": mode, "value": mode} for mode in appointment_modes],
        placeholder="Filter by mode (optional)",
        id="mode-filter",
        clearable=True
    ),

    dcc.Graph(id='mode-line'),

    html.Hr(),

    dcc.Graph(
        figure=px.bar(
            appointments_by_season,
            x='Season',
            y='count_of_appointments',
            title='Total NHS Appointments by Season',
            labels={'count_of_appointments': 'Appointments'}
        )
    )

], fluid=True)

@app.callback(
    Output("mode-line", "figure"),
    Input("mode-filter", "value")
)
def update_line_chart(selected_mode):
    df = appointments_by_mode.copy()
    if selected_mode:
        df = df[df['appointment_mode'] == selected_mode]
    fig = px.line(df, x="appointment_month", y="count_of_appointments", color="appointment_mode",
                  title="Appointments Over Time by Mode",
                  labels={'appointment_month': 'Month', 'count_of_appointments': 'Appointments'})
    return fig

if __name__ == "__main__":
    app.run(debug=True)

