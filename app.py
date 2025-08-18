from hike_logger import create_app, db
from hike_logger import models
import requests

app = create_app()
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

