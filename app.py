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
        f"/api/v1.0/<start>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    start_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    rain = session.query(measurement.date, measurement.prcp).filter(measurement.date >= start_date).all()
    session.close()

    precipitation_list = []
    for date, prcp in rain:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation_list.append(precipitation_dict)

    return(jsonify(precipitation_list))

@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(station.station).all()
    session.close()

    station_list = []
    for station in stations:
        station_list.append(station)

    return(jsonify(station_list))

@app.route("/api/v1.0/tobs")
def tobs():

    station_activity = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    most_active_station_id = station_activity[0][0]

    start_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)

    tobs = session.query(measurement.date, measurement.tobs).filter(measurement.date >= start_date).filter(measurement.station == most_active_station_id).all()
    session.close()

    tobs_list = []
    for date, tob in tobs:
        tobs_dict={}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tob
        tobs_list.append(tobs_dict)

    return(jsonify(tobs_list))

@app.route("/api/v1.0/<start>")
def start(start):

    tmin = session.query(measurement.date, func.min(measurement.tobs)).filter(measurement.date >= start).all()

    session.close()

    summary_list = []
    for date, temp in tmin:
        summary_dict={}
        summary_dict["date"] = date
        summary_dict["temp"] = temp
        summary_list.append(summary_dict)

    return(jsonify(summary_list))

if __name__ == "__main__":
    app.run(debug=True)