# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import join

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
    return (
        # Routes are formatted, and titles are added for easier navigation
        f"<b>Available Routes:</b><br/><br/>"

        f"<b>Precipitation Analysis</b> (for the last 12 months)<br/>"
        f"/api/v1.0/precipitation<br/><br/>"

        f"<b>Stations</b><br/>"
        f"/api/v1.0/stations<br/><br/>"

        f"<b>Temperature Observations</b> (for the most active station, in the last 12 months)<br/>"
        f"/api/v1.0/tobs<br/><br/>"

        # Formatting is specified for start and end dates 
        f"<b>Temperature Summary</b>, from specified start date (format yyyy-mm-dd) (inclusive)<br/>"
        f"/api/v1.0/<start><br/><br/>"

        f"<b>Temperature Summary</b>, from specified start date to specified end date (format yyyy-mm-dd/yyyy-mm-dd) (inclusive)<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Date and prcp values are obtained from database, with a date filter added on
    # Start date is not passed as a variable in the query
    prcp_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= "2016-08-23").all()

    # Session is closed after each query
    session.close()

    # Empty list is set up
    precipitation_list = []

    # "For loop" to cycle through query data
    for date, prcp in prcp_data:

        # Empty dictionary is set up for each element
        precipitation_dict = {}

        # Dictionary element is created, with "date" and "prcp" as keys, and their corresponding values as values
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp

        # Dictionary element is appended to to list
        precipitation_list.append(precipitation_dict)

    # Data is returned as a jsonified list of dictionaries
    return(jsonify(precipitation_list))

@app.route("/api/v1.0/stations")
def stations():

    # The query and dictionary process is repeated for each route
    station_data = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()

    station_list = []
    for id, name, lat, lng, elev in station_data:
        station_dict = {}
        station_dict["station"] = id
        station_dict["name"] = name
        station_dict["lat"] = lat
        station_dict["lng"] = lng
        station_dict["elevation"] = elev
        station_list.append(station_dict)

    return(jsonify(station_list))

@app.route("/api/v1.0/tobs")
def tobs():

    # The most active station is obtained using func.count
    # Stations are grouped by station id, then the count is taken
    # The query is then ordered by decreasing station count
    station_activity = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()

    # Most active station is obtained by indexing of previous station_activity query
    most_active_station_id = station_activity[0][0]

    # Date and tobs values are obtained, with a filters applied to only query dates after a specified start date, and to only query the most active station
    tobs_data = session.query(measurement.date, measurement.tobs).filter(measurement.date >= "2016-08-23").filter(measurement.station == most_active_station_id).all()
    session.close()

    tobs_list = []
    for date, tob in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tob
        tobs_list.append(tobs_dict)

    return(jsonify(tobs_list))

@app.route("/api/v1.0/<start>")

# Start date (obtained from the url) is passed through class
def start(start):

    # Temperatures are grouped by date, and func.min, func.avg, and func.max are used to obtain minimum, average, and maximum temperatures, with a filter applied to only query dates after a specified start date
    temp_summary_data = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()
    session.close()

    summary_list = []
    for date, tmin, tavg, tmax in temp_summary_data:
        summary_dict = {}
        summary_dict["date"] = date
        summary_dict["TMIN"] = tmin
        summary_dict["TAVG"] = round(tavg,1)
        summary_dict["TMAX"] = tmax

        summary_list.append(summary_dict)

    return(jsonify(summary_list))

@app.route("/api/v1.0/<start>/<end>")

# Start and end dates (obtained from the url) are passed through class
def start_end(start, end):

    # Temperatures are grouped by date, and func.min, func.avg, and func.max are used to obtain minimum, average, and maximum temperatures, with filters applied to only query dates between 2 given dates.
    temp_summary_data = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date<= end).group_by(measurement.date).all()
    session.close()

    summary_list = []
    for date, tmin, tavg, tmax in temp_summary_data:
        summary_dict = {}
        summary_dict["date"] = date
        summary_dict["TMIN"] = tmin
        summary_dict["TAVG"] = round(tavg,1)
        summary_dict["TMAX"] = tmax

        summary_list.append(summary_dict)

    return(jsonify(summary_list))

if __name__ == "__main__":
    app.run(debug=True)