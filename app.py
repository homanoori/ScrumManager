from flask import Flask, render_template
from database import init_db

from routes.hamed_routes import hamed_bp
from routes.homa_routes import homa_bp
from routes.setayesh_routes import setayesh_bp
from routes.sasan_routes import sasan_bp

app = Flask(__name__)

app.register_blueprint(hamed_bp)
app.register_blueprint(homa_bp)
app.register_blueprint(setayesh_bp)
app.register_blueprint(sasan_bp)

@app.route("/")
def index():
    return render_template("base.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)