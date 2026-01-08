from flask import Flask
from flask_mysqldb import MySQL
from flask_socketio import SocketIO

mysql = MySQL()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'rahasia_negara'
    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'
    
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'social_media_db'
    
    app.config['MYSQL_CHARSET'] = 'utf8mb4' 

    mysql.init_app(app)
    socketio.init_app(app)

    from .main.routes import main
    from .auth.routes import auth
    
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app