# Import the dependencies.

from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################

#Create engine

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station

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
    """Homepage route."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON representation of precipitation data."""
    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp)\
                     .order_by(Measurement.date.desc())\
                     .limit(365).all()
    # Convert results to dictionary
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return JSON list of stations."""
    # Query all stations
    results = session.query(Station.station).all()
    # Convert results to list
    station_list = [station for (station,) in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return JSON list of temperature observations for the most active station."""
    # Query the last 12 months of temperature observations for the most active station
    most_active_station = session.query(Measurement.station)\
                                  .group_by(Measurement.station)\
                                  .order_by(func.count(Measurement.station).desc())\
                                  .first()[0]

    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.station == most_active_station)\
                     .order_by(Measurement.date.desc())\
                     .limit(365).all()
    # Convert results to list of dictionaries
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return JSON list of TMIN, TAVG, and TMAX for dates greater than or equal to start date."""
    # Query for TMIN, TAVG, and TMAX
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start).all()
    # Convert results to list of dictionaries
    temp_stats = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return JSON list of TMIN, TAVG, and TMAX for dates between start and end date, inclusive."""
    # Query for TMIN, TAVG, and TMAX
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                     .filter(Measurement.date >= start)\
                     .filter(Measurement.date <= end).all()
    # Convert results to list of dictionaries
    temp_stats = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in results]
    return jsonify(temp_stats)

# Run the app
if __name__ == "__main__":
    app.run()