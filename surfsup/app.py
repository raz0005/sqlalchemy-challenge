# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup
app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii Climate API<br>"
        f"Here are all the available API routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start> (enter as YYYY-MM-DD)<br>"
        f"/api/v1.0/<start>/<end> (enter as YYYY-MM-DD/YYYY-MM-DD)<br>"
    )

#Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    previous_year = dt.date(year.year, year.month, year.day)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date>=previous_year).order_by(measurement.date.desc()).all()
    precipitation_dict = dict(results)

    precipitation_dict = {date: prcp for date, prcp in results}
    print(f"The results for Percipitation: {precipitation_dict}")
    return jsonify(precipitation_dict)

#Stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_results = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    session.close()

    stations_list = []
    for station_id,name,latitude,longitude,elevation in station_results:
        station_dict = {}
        station_dict['station_id'] = station_id
        station_dict['Lat'] = latitude
        station_dict['Lon'] = longitude
        station_dict['Elevation'] = elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

#Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    tobs_results = session.query(measurement.date, measurement.tobs).filter(measurement.station=='USC00519281').filter(measurement.date>='2016-08-23').all()

    tobs_list = []
    for date, tobs in tobs_results:
        tobs_dict={}
        tobs_dict['Date']=date
        tobs_dict['Tobs']=tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs)

#Stations
@app.route("/api/v1.0/stats")
def station():
    session = Session(engine)

    # Calculate temperature statistics
    results = (
        session.query(
            func.min(measurement.tobs),
            func.max(measurement.tobs),
            func.avg(measurement.tobs)
        )
        .filter(measurement.station == "USC00519281")
        .all()
    )
    session.close()

    stats_dict = {
        "Lowest Temperature": results[0][0],
        "Highest Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }
    return jsonify(stats_dict)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    
    # Query temperature statistics from the start date
    results = (
        session.query(
            func.min(measurement.tobs),
            func.max(measurement.tobs),
            func.avg(measurement.tobs)
        )
        .filter(measurement.date >= start)
        .all()
    )
    session.close()

    # Create a dictionary to hold the results
    stats_dict = {
        "Start Date": start,
        "Lowest Temperature": results[0][0],
        "Highest Temperature": results[0][1],
        "Average Temperature": results[0][2]
    }
    return jsonify(stats_dict)

#Start/End
@app.route("/api/v1.0/<start>/<end>")
def start_end_temps(start,end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    temps=[]
    for min_temp,avg_temp,max_temp in results:
        temp_dict = {}
        temp_dict['Minimum Temp']= min_temp
        temp_dict['Average Temp']= avg_temp
        temp_dict['Maximum Temp']=max_temp
        temps.append(temp_dict)
    return jsonify(temps)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
