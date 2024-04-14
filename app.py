# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Welcome to the homepage!")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    start_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    rain = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).all()

    precipitation_list = []
    for date, prcp in rain:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)

    return(jsonify(precipitation_list))

@app.route("/api/v1.0/stations")
def stations():

    station_activity = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    station_list = []
    for station, count in station_activity:
        station_list.append(station)

    return(jsonify(station_list))

@app.route("/api/v1.0/tobs")
def tobs():
    return("tobs")

if __name__ == "__main__":
    app.run(debug=True)