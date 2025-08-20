from hike_logger import create_app, db
from hike_logger import models
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime

app = create_app()
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

