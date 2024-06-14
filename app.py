import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import psycopg2
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__,
                requests_pathname_prefix="/webapp-DW1/",
                routes_pathname_prefix="/webapp-DW1/")

KEY_VAULT_URL = "https://fsdh-proj-dw1-poc-kv.vault.azure.net/"
error_occur = False

try:
    # Retrieve the secrets containing DB connection details
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

    # Retrieve the secrets containing DB connection details
    DB_NAME = "fsdh"
    DB_HOST = secret_client.get_secret("datahub-psql-server").value
    DB_USER = secret_client.get_secret("datahub-psql-admin").value
    DB_PASS = secret_client.get_secret("datahub-psql-password").value
except Exception as e:
    error_occur = True
    print(f"An error occurred: {e} | Une erreur s'est produite: {e}")

# Define the layout of the app
app.layout = html.Div([
    html.H1('Sample FSDH Dash Application | Exemple d\'une application Dash sur le DHSF'),
    # Form 1 - Query database
    html.H2('Celestial Body Database Query | Requête de la base de données des corps célestes'),
    html.P('The database contains information about celestial bodies. Enter the name of a celestial body to query the database. | La base de données contient des informations sur les corps célestes. Entrez le nom d\'un corps céleste pour interroger la base de données.'),
    dcc.Input(id='query-name', type='text', placeholder='Celestial body name | Nom du corps céleste'),
    html.Button('Query Database | Interroger la base de données', id='query-button', n_clicks=0),
    html.Div(id='query-output'),

    # Figure 1 - Plot celestial bodies
    html.H3('Celestial Bodies Plot | Tracé des corps célestes'),
    html.P('The plot shows the mass of celestial bodies against their distance from the sun. | Le graphique montre la masse des corps célestes par rapport à leur distance par rapport au soleil.'),
    dcc.Graph(id='celestial-bodies-plot'),

    # Form 2 - Add new celestial body
    html.H1('Add New Celestial Body | Ajouter un nouveau corps céleste'),
    html.P('Add a new celestial body to the database. | Ajoutez un nouveau corps céleste à la base de données.'),
    dcc.Input(id='add-name', type='text', placeholder='Name | Nom'),
    dcc.Input(id='add-type', type='text', placeholder='Type | Type'),
    dcc.Input(id='add-radius', type='number', placeholder='Radius | Rayon'),
    dcc.Input(id='add-mass', type='number', placeholder='Mass | Masse'),
    dcc.Input(id='add-distance', type='number', placeholder='Distance from sun | Distance par rapport au soleil'),
    html.Button('Add Celestial Body | Ajouter un corps céleste', id='add-button', n_clicks=0),
    html.Div(id='add-output'),

    # Form 3 - Delete celestial body by ID
    html.H1('Delete Celestial Body | Supprimer un corps céleste'),
    html.P('Delete a celestial body from the database by ID. | Supprimez un corps céleste de la base de données par ID.'),
    dcc.Input(id='delete-id', type='number', placeholder='ID'),
    html.Button('Delete Celestial Body | Supprimer un corps céleste', id='delete-button', n_clicks=0),
    html.Div(id='delete-output')
    
], style={'width': '50%', 'margin': 'auto', 'font-family': 'Arial, sans-serif'})

# Define callback to delete a celestial body from the database
@app.callback(
    Output('delete-output', 'children'),
    [Input('delete-button', 'n_clicks')],
    [State('delete-id', 'value')]
)
def delete_celestial_body(n_clicks, id):
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        
        # Create a new cursor
        cur = conn.cursor()
        
        # Run the query
        cur.execute("DELETE FROM celestial_bodies WHERE id = %s", (id,))
        conn.commit()
        
        # Close the cursor and connection to the database
        cur.close()
        conn.close()
        
        return "Celestial body deleted successfully."
    else:
        return ""

# Define callback to plot celestial bodies
@app.callback(
    Output('celestial-bodies-plot', 'figure'),
    [Input('query-button', 'n_clicks')],
    [State('query-name', 'value')]
)
def plot_celestial_bodies(n_clicks, name):
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        
        # Create a new cursor
        cur = conn.cursor()
        
        # Run the query
        cur.execute("SELECT * FROM celestial_bodies WHERE name LIKE '%{}%'".format(name))
        result = cur.fetchall()
        
        # Close the cursor and connection to the database
        cur.close()
        conn.close()

        # Convert query result to DataFrame
        df = pd.DataFrame(result, columns=['id', 'name', 'type', 'radius', 'mass', 'distance from sun'])

        # Create a scatter plot
        fig = {
            'data': [
                {
                    'x': df['distance from sun'],
                    'y': df['mass'],
                    'text': df['name'],
                    'mode': 'markers'
                }
            ],
            'layout': {
                'title': 'Celestial Bodies',
                'xaxis': {'title': 'Distance from sun (km)'},
                'yaxis': {'title': 'Mass (kg)'}
            }
        }

        return fig
    else:
        return {}
    

# Define callback to insert a new celestial body into the database
@app.callback(
    Output('add-output', 'children'),
    [Input('add-button', 'n_clicks')],
    [State('add-name', 'value'),
     State('add-type', 'value'),
     State('add-radius', 'value'),
     State('add-mass', 'value'),
     State('add-distance', 'value')]
)
def add_celestial_body(n_clicks, name, type, radius, mass, distance):
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        
        # Create a new cursor
        cur = conn.cursor()
        
        # Run the query
        cur.execute("INSERT INTO celestial_bodies (name, body_type, mean_radius_km, mass_kg, distance_from_sun_km) VALUES (%s, %s, %s, %s, %s)", (name, type, radius, mass, distance))
        conn.commit()
        
        # Close the cursor and connection to the database
        cur.close()
        conn.close()
        
        return "Celestial body added successfully."
    else:
        return ""


# Define callback to update the output div with the query result
@app.callback(
    Output('query-output', 'children'),
    [Input('query-button', 'n_clicks')],
    [State('query-name', 'value')]
)
def get_celestial_body(n_clicks, name):
    if n_clicks > 0:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST
        )
        
        # Create a new cursor
        cur = conn.cursor()
        
        # Run the query
        cur.execute("SELECT * FROM celestial_bodies WHERE name LIKE '%{}%'".format(name))
        result = cur.fetchall()
        
        # Close the cursor and connection to the database
        cur.close()
        conn.close()

        # Convert query result to DataFrame, then to a HTML table
        if result:
            df = pd.DataFrame(result, columns=['id', 'name', 'type', 'radius', 'mass', 'distance from sun'])  # Replace with actual column names
            return html.Table(
                # Header
                [html.Tr([html.Th(col, style={'border': '1px solid black', 'padding': '8px'}) for col in df.columns])] +

                # Body
                [html.Tr([
                    html.Td(df.iloc[i][col], style={'border': '1px solid black', 'padding': '8px'}) for col in df.columns
                ]) for i in range(len(df))]
            )
        else:
            return "No celestial bodies found with that name."
    else:
        return ""

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=80)