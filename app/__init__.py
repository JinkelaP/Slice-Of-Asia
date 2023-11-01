from flask import Flask
from flask_mysqldb import MySQL
from flask_socketio import SocketIO
from flask_cors import CORS

from . import index

# from app import yourPyFileName
# from app import login,admin,logout
# from app import temporaryIndex

mysql = MySQL()
socketio = SocketIO(cors_allowed_origins=["http://127.0.0.1:5000", "http://localhost:5000"])

def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app, origin=["http://127.0.0.1:5000", "http://localhost:5000"])
    app.secret_key = 'group1-project2'

    # Configure mysql database
    app.config['MYSQL_HOST'] = '127.0.0.1'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'lincoln2023'
    app.config['MYSQL_DB'] = 'takeaway'
    app.config['MYSQL_PORT'] = 3306
    
    mysql.init_app(app) 
    socketio.init_app(app)

    from . import login, logout, reg, adminDashboard1, adminDashboard2, staffDashboard, customerDashboard, index
    # import the Blueprints
    app.register_blueprint(login.bp)
    app.register_blueprint(reg.bp)
    app.register_blueprint(logout.bp)
    app.register_blueprint(index.bp)
    app.register_blueprint(adminDashboard1.bp)
    app.register_blueprint(adminDashboard2.bp)
    app.register_blueprint(staffDashboard.bp)
    app.register_blueprint(customerDashboard.bp)



    return app