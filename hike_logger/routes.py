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
        
        # Check if user wants to review gear after adding trip
        if request.form.get('review_after') and selected_gear_ids:
            return redirect(url_for("main.review_gear", trip_id=new_trip.id))
        
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

@main.route("/gear")
def gear_list():
    try:
        gear = Gear.query.order_by(Gear.category, Gear.name).all()
        print(f"DEBUG: Found {len(gear)} gear items")
        for g in gear:
            print(f"DEBUG: Gear - {g.name} ({g.category})")
        return render_template("gear_list.html", gear=gear)
    except Exception as e:
        print(f"ERROR in gear_list route: {e}")
        return render_template("gear_list.html", gear=[])

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

@main.route("/trip/<int:trip_id>/review_gear", methods=["GET", "POST"])
def review_gear(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    trip_gear_items = TripGear.query.filter_by(trip_id=trip_id).all()
    
    if not trip_gear_items:
        return redirect(url_for("main.trip_detail", trip_id=trip_id))
    
    if request.method == "POST":
        for trip_gear in trip_gear_items:
            gear_id = trip_gear.gear_id
            
            # Get form data for this specific gear item
            overall_rating = request.form.get(f"overall_rating_{gear_id}")
            comfort_rating = request.form.get(f"comfort_rating_{gear_id}")
            durability_rating = request.form.get(f"durability_rating_{gear_id}")
            weather_performance = request.form.get(f"weather_performance_{gear_id}")
            performance_notes = request.form.get(f"performance_notes_{gear_id}")
            had_issues = request.form.get(f"had_issues_{gear_id}")
            issue_description = request.form.get(f"issue_description_{gear_id}")
            would_bring_again = request.form.get(f"would_bring_again_{gear_id}")
            
            # Update the TripGear record
            trip_gear.overall_rating = int(overall_rating) if overall_rating else None
            trip_gear.comfort_rating = int(comfort_rating) if comfort_rating else None
            trip_gear.durability_rating = int(durability_rating) if durability_rating else None
            trip_gear.weather_performance = int(weather_performance) if weather_performance else None
            trip_gear.performance_notes = performance_notes
            trip_gear.had_issues = bool(had_issues)
            trip_gear.issue_description = issue_description if had_issues else None
            trip_gear.would_bring_again = bool(would_bring_again)
        
        db.session.commit()
        return redirect(url_for("main.trip_detail", trip_id=trip_id))
    
    return render_template("review_gear.html", trip=trip, trip_gear_items=trip_gear_items)

@main.route("/gear/<int:gear_id>/performance")
def gear_performance_history(gear_id):
    gear = Gear.query.get_or_404(gear_id)
    
    # Get all trip performances for this gear
    performances = db.session.query(TripGear, Trip).join(Trip).filter(
        TripGear.gear_id == gear_id
    ).order_by(Trip.date.desc()).all()
    
    return render_template("gear_performance.html", gear=gear, performances=performances)