from . import db
class Gear(db.Model):
    __tablename__ = 'gear'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    weight_grams = db.Column(db.Integer)
    notes = db.Column(db.Text)

    trips = db.relationship('TripGear', back_populates='gear')

    def __repr__(self):
        return f"<Gear {self.name} ({self.category})>"
    
    def average_rating(self):
        """Calculate average performance rating across all trips."""
        ratings = [tg.overall_rating for tg in self.trips if tg.overall_rating]
        return round(sum(ratings) / len(ratings), 1) if ratings else None
    
class Trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100))
    distance_km = db.Column(db.Float)
    elevation_gain_m = db.Column(db.Integer)
    weather = db.Column(db.String(100))
    notes = db.Column(db.Text)

    gear_items = db.relationship('TripGear', back_populates='trip')

    def __repr__(self):
        return f"<Trip {self.name} on {self.date}>"
    
class TripGear(db.Model):
    __tablename__ = 'trip_gear'
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    gear_id = db.Column(db.Integer, db.ForeignKey('gear.id'), nullable=False)
    
    # Performance tracking fields
    overall_rating = db.Column(db.Integer)  # 1-5 scale
    comfort_rating = db.Column(db.Integer)  # 1-5 scale
    durability_rating = db.Column(db.Integer)  # 1-5 scale
    weather_performance = db.Column(db.Integer)  # 1-5 scale
    
    # Specific performance notes
    performance_notes = db.Column(db.Text)
    # Issues encountered
    had_issues = db.Column(db.Boolean, default=False)
    issue_description = db.Column(db.Text)
    
    # Would you bring it again on similar trips?
    would_bring_again = db.Column(db.Boolean)
    

    trip = db.relationship('Trip', back_populates='gear_items')
    gear = db.relationship('Gear', back_populates='trips')

    def __repr__(self):
        return f"<TripGear TripID={self.trip_id} GearID={self.gear_id}"