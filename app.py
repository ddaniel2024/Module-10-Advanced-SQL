# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

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
    return("ROUTES")

@app.route("/api/v1.0/precipitation")
def precipitation():
    return("prcp JSON")

@app.route("/api/v1.0/stations")
def stations():
    return("stations")

@app.route("/api/v1.0/tobs")
def tobs():
    return("tobs")

if __name__ == "__main__":
    app.run(debug=True)