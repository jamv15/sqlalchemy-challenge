# Import the dependencies.

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta 
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route('/', methods=['GET'])
def home():
    return (
        "<h1>Welcome to the Hawaii Climate API!</h1>"
        "<p>Available Routes:</p>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>Precipitation Data</a></li>"
        "<li><a href='/api/v1.0/stations'>Station Data</a></li>"
        "<li><a href='/api/v1.0/tobs'>Temperature Observations</a></li>"
        "<li><a href='/api/v1.0/start'>Temperature Summary (start date)</a></li>"
        "<li><a href='/api/v1.0/start/end'>Temperature Summary (start-end date range)</a></li>"
        "</ul>"
    )

@app.route("/api/v1.0/precipitation", methods=['GET'])
def precipitation():
    session = Session(engine)
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_ago = most_recent_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= one_year_ago
    ).all()
    
    session.close()
    
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations", methods=['GET'])
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()
    
    # Convert results to a list of dictionaries
    stations_list = [{'station': station, 'name': name} for station, name in results]
    
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs', methods=['GET'])
def tobs():
    session = Session(engine)

    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')

    one_year_ago = most_recent_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago
    ).all()

    session.close()

    temperatures = [tobs for date, tobs in results]

    return jsonify(temperatures)

@app.route('/api/v1.0/<start>', methods=['GET'])
def start_date(start):
    session = Session(engine)

    # Query the minimum, average, and maximum temperatures from the start date
    results = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date >= start).all()

    session.close()

    temp_summary = {
        'Start Date': start,
        'TMIN': results[0].TMIN,
        'TAVG': results[0].TAVG,
        'TMAX': results[0].TMAX
    }

    return jsonify(temp_summary)

@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def start_end_dates(start, end):
    session = Session(engine)
    results = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date >= start, Measurement.date <= end).all()

    session.close()

    temp_summary = {
        'Start Date': start,
        'End Date': end,
        'TMIN': results[0].TMIN,
        'TAVG': results[0].TAVG,
        'TMAX': results[0].TMAX
    }

    return jsonify(temp_summary)

if __name__ == '__main__':
    app.run(debug=True)