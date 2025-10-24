import os
from src.dashboard import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('APP_PORT', 8050))
    app.run_server(host='0.0.0.0', port=port, debug=True)
