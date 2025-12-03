from dash import Dash
from src.dashboard import create_dashboard

# Inicializa o app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Netflix Dashboard"

# Cria layout e callbacks
create_dashboard(app)

if __name__ == "__main__":
    # Dash 3.x usa app.run()
    app.run(debug=True)


