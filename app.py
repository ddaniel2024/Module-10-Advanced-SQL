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
engine = create_engine(f'sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"<b>Available Routes:</b><br/><br/>"

        f"<b>Precipitation Analysis</b> (for the last 12 months)<br/>"
        f"/api/v1.0/precipitation<br/><br/>"

        f"<b>Stations</b><br/>"
        f"/api/v1.0/stations<br/><br/>"

        f"<b>Temperature Observations</b> (for the most active station, in the last 12 months)<br/>"
        f"/api/v1.0/tobs<br/><br/>"

        f"<b>Temperature Summary</b>, from specified start date (format yyyy-mm-dd) (inclusive)<br/>"
        f"/api/v1.0/<start><br/><br/>"

        f"<b>Temperature Summary</b>, from specified start date to specified end date (format yyyy-mm-dd/yyyy-mm-dd) (inclusive)<br/>"
        f"/api/v1.0/<start>/<end>"
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

    station = Base.classes.station
    session = Session(engine)

    stations = session.query(station.station, station.name).all()

    station_list = []
    for station, name in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_list.append(station_dict)

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
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tob
        tobs_list.append(tobs_dict)

    return(jsonify(tobs_list))

@app.route("/api/v1.0/<start>")
def start(start):

    temps = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()
    session.close()

    summary_list = []
    for date, tmin, tavg, tmax in temps:
        summary_dict = {}
        summary_dict["date"] = date
        summary_dict["TMIN"] = tmin
        summary_dict["TAVG"] = round(tavg,1)
        summary_dict["TMAX"] = tmax

        summary_list.append(summary_dict)

    return(jsonify(summary_list))

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    temps = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date<= end).group_by(measurement.date).all()
    session.close()

    summary_list = []
    for date, tmin, tavg, tmax in temps:
        summary_dict = {}
        summary_dict["date"] = date
        summary_dict["TMIN"] = tmin
        summary_dict["TAVG"] = round(tavg,1)
        summary_dict["TMAX"] = tmax

        summary_list.append(summary_dict)

    return(jsonify(summary_list))

if __name__ == "__main__":
    app.run(debug=True)