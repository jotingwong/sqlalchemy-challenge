# Author: JoTing Wong

import numpy as np

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
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end></br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a Dictionary using date as the key and prcp as the value"""
    # Query mesurement dataset
    precipitation = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    all_precipitation = []
    for date, prcp in precipitation:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query station dataset
    station = session.query(Station.station,Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_station = []
    for station, name in station:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_station.append(station_dict)

    return jsonify(all_station)


# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    # Query Measurement dataset

    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date

    last12_months = dt.datetime.strptime(max_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores

    ly_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last12_months).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_tobs = []
    for date, tobs in ly_tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def start_end(start=None, end=None):

    session = Session(engine)
    """Return a list of min, avg, max for specific dates"""

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:

        start= session.query(*sel).filter(Measurement.date >= start).all()

        temp_start = list(np.ravel(start))

        return jsonify(temp_start)

    

    end = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temp_end = list(np.ravel(end))

    return jsonify(temp_end)



if __name__ == '__main__':
    app.run(debug=True)
