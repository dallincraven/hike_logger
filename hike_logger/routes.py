from flask import Blueprint, render_template, request, redirect, url_for
from .models import Trip, Gear, TripGear
from datetime import datetime
from . import db


main = Blueprint('main', __name__)

@main.route("/")
def index():
    trips = Trip.query.order_by(Trip.date.desc()).all()
    return render_template('index.html', trips=trips)

@main.route("/add_trip", methods=["GET", "POST"])
def add_trip():
    if request.method == "POST":
        name = request.form.get("name")
        date_str = request.form.get("date")
        location = request.form.get("location")
        distance_km = request.form.get("distance_km")
        elevation_gain_m = request.form.get("elevation_gain_m")
        weather = request.form.get("weather")
        notes = request.form.get("notes")

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        distance_km = float(distance_km) if distance_km else None
        elevation_gain_m = int(elevation_gain_m) if elevation_gain_m else None

        new_trip = Trip(
            name=name,
            date=date,
            location=location,
            distance_km=distance_km,
            elevation_gain_m=elevation_gain_m,
            weather=weather,
            notes=notes
        )

        db.session.add(new_trip)
        db.session.commit()

        return redirect(url_for("main.index"))
    return render_template("add_trip.html")
