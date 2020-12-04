from dfo_app import app
from dfo_app.routes import socketio
socketio.run(app,debug=True)
