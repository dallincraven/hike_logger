from flask import Blueprint, render_template, request, redirect, url_for
from .models import Trip, Gear, TripGear
from datetime import datetime
from . import db


main = Blueprint('main', __name__)

@main.route("/")
def index():
    if not db.session.query(Trip).first():
        return redirect(url_for("main.add_trip"))
    trips = Trip.query.order_by(Trip.date.desc()).all()
    gear = Gear.query.order_by(Gear.name).all()
    return render_template('index.html', trips=trips, gear=gear)

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
        
        # Get selected gear IDs
        selected_gear_ids = request.form.getlist("gear_ids")

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
        db.session.flush()  # This gets the ID without committing

        # Add gear associations
        for gear_id in selected_gear_ids:
            if gear_id:  # Make sure it's not empty
                trip_gear = TripGear(trip_id=new_trip.id, gear_id=int(gear_id))
                db.session.add(trip_gear)

        db.session.commit()
        return redirect(url_for("main.index"))
    
    # For GET request, pass all gear to template
    gear = Gear.query.order_by(Gear.category, Gear.name).all()
    return render_template("add_trip.html", gear=gear)

@main.route("/add_gear", methods=["GET","POST"])
def add_gear():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        weight_grams = request.form.get("weight_grams")
        notes = request.form.get("notes")

        weight_grams = int(weight_grams) if weight_grams else None

        new_gear = Gear(
            name=name,
            category=category,
            weight_grams=weight_grams,
            notes=notes
        )

        db.session.add(new_gear)
        db.session.commit()

        return redirect(url_for("main.index"))
    return render_template("add_gear.html")

@main.route("/trip/<int:trip_id>")
def trip_detail(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    # Get all gear used on this trip
    gear_used = db.session.query(Gear).join(TripGear).filter(TripGear.trip_id == trip_id).all()
    
    # Calculate total weight if you want
    total_weight = sum(gear.weight_grams for gear in gear_used if gear.weight_grams)
    
    return render_template('trip_detail.html', trip=trip, gear_used=gear_used, total_weight=total_weight)

@main.route("/edit_trip/<int:trip_id>", methods=["GET", "POST"])
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == "POST":
        # Update trip details
        trip.name = request.form.get("name")
        trip.location = request.form.get("location")
        trip.date = datetime.strptime(request.form.get("date"), "%Y-%m-%d").date()
        trip.distance_km = float(request.form.get("distance_km")) if request.form.get("distance_km") else None
        trip.elevation_gain_m = int(request.form.get("elevation_gain_m")) if request.form.get("elevation_gain_m") else None
        trip.weather = request.form.get("weather")
        trip.notes = request.form.get("notes")
        
        # Update gear associations
        selected_gear_ids = request.form.getlist("gear_ids")
        
        # Remove existing gear associations
        TripGear.query.filter_by(trip_id=trip_id).delete()
        
        # Add new gear associations
        for gear_id in selected_gear_ids:
            if gear_id:
                trip_gear = TripGear(trip_id=trip_id, gear_id=int(gear_id))
                db.session.add(trip_gear)
        
        db.session.commit()
        return redirect(url_for("main.trip_detail", trip_id=trip_id))
    
    # For GET request
    gear = Gear.query.order_by(Gear.category, Gear.name).all()
    current_gear_ids = [tg.gear_id for tg in trip.gear_items]
    
    return render_template("edit_trip.html", trip=trip, gear=gear, current_gear_ids=current_gear_ids)