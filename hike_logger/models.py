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

    trip = db.relationship('Trip', back_populates='gear_items')
    gear = db.relationship('Gear', back_populates='trips')

    def __repr__(self):
        return f"<TripGear TripID={self.trip_id} GearID={self.gear_id}"