import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Create engine
engine = create_engine('sqlite:///hawaii.sqlite')

Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurements
Station = Base.classes.stations

# Create session
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def Hawaii():
    return (
        f"<p>Hawaii weather API</p>"
        f"<p>Usage:</p>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of percipitation data from the past year<br/><br/>"
        f"/api/v1.0/stations<br/>Return a JSON list of stations from the dataset<br/><br/>"
        f"/api/v1.0/tobs<br/>Return a JSON list of temperature observations from the previous year<br/><br/>"
        f"/api/v1.0/date<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and 8/23/17<br/><br/>."
        f"/api/v1.0/start_date/end_date<br/>Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range<br/><br/>."
    )

# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value
    recent_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)

# Return the JSON representation of your dictionary
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago, Measurement.prcp != None).\
    order_by(Measurement.date).all()
    return jsonify(dict(prcp_data))

# /api/v1.0/stations
#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    stations_data = session.query(Station.station, Station.name).all()
    return jsonify(stations_data)

# /api/v1.0/tobs
#Query the dates and temperature observations of the most-active station for the previous year of data
@app.route("/api/v1.0/tobs")
def tobs_most_active():
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)
    tobs_data = session.query(Measurement.tobs).\
        filter(Measurement.date >= one_year_ago, Measurement.station == 'USC00519281').\
        order_by(Measurement.tobs).all()
    return jsonify(tobs_data)

# Return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_prev_year = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= '2016-08-23').all()
    return jsonify(tobs_prev_year)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
@app.route("/api/v1.0/<date>")
def only_start(date):
    start_temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= date).all()
    return jsonify(start_temp_data)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    start_end_temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(start_end_temp_data)