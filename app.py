from dash import Dash
from src.dashboard import create_dashboard

app = Dash(__name__)
create_dashboard(app)

if __name__ == "__main__":
    app.run(debug=True)
