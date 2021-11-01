# Import dependancies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


from flask import Flask, jsonify

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

# Create our session (link) from Python to the DB
session = Session(engine)

# Find the most recent date in the data set.
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
recent_date

# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Starting from the most recent data point in the database. 
recent_date_dt = dt.datetime.strptime(recent_date, "%Y-%m-%d")
# Calculate the date one year from the last date in data set.
one_yr_earlier = recent_date_dt - dt.timedelta(days=365)
one_yr_earlier_dt = dt.datetime.strftime(one_yr_earlier,"%Y-%m-%d")

# Close the session
session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    prcp_scores_query = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date > one_yr_earlier_dt).\
        order_by(Measurement.date).all()

    session.close()

    # Convert query results to dictionary
    date_list = []
    prcp_list = []


    for line in prcp_scores_query:
        date_list.append(line[0])
        prcp_list.append(line[1])

    precipitation_dict = dict(zip(date_list,prcp_list))

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations ():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    station_query = session.query(Measurement.station).\
    group_by(Measurement.station).all()

    session.close()
    
    # Create list of stations
    station_list = []
    for station in station_query:
        station_list.append(station[0])

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs ():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    most_active_last_12 = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station =='USC00519281').\
    filter(Measurement.date > one_yr_earlier_dt).all()

    session.close()
    
    # Create list of temperature
    temp_list = []
    for temp in most_active_last_12:
        temp_list.append(temp[1])

    return jsonify(temp_list)

@app.route('/api/v1.0/<start>')
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    tmin_tavg_tmax = session.query(func.min(Measurement.tobs),\
     func.avg(Measurement.tobs),\
     func.max(Measurement.tobs)).\
    filter(Measurement.date <= start_date).all()

    tmin_tavg_tmax_list = [i for i in tmin_tavg_tmax[0]]

    session.close()

    return jsonify(tmin_tavg_tmax_list)

@app.route('/api/v1.0/<start>/<end>')
def start(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp information
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    tmin_tavg_tmax = session.query(func.min(Measurement.tobs),\
     func.avg(Measurement.tobs),\
     func.max(Measurement.tobs)).\
    filter(Measurement.date <= start_date).\
    filter(Measurement.date >= end_date).all()

    tmin_tavg_tmax_list = [i for i in tmin_tavg_tmax[0]]

    session.close()

    return jsonify(tmin_tavg_tmax_list)

if __name__ == "__main__":
    app.run(debug=True)
