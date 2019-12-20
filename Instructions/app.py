#importing dependencies for python flask module 

from flask import Flask, jsonify

#importing dependencies from sqlalchemy to connect to DataBase in the back end

import sqlalchemy
from sqlalchemy import create_engine,func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#importing dependencies for python
import numpy as np
import os
import datetime as dt
from dateutil.relativedelta import relativedelta

#setting up DataBase

engine = create_engine(os.path.join("sqlite:///","Resources","hawaii.sqlite"))

#reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine,reflect=True)

#Save table refernces

Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask setup

app = Flask(__name__)

#Flask routes 

@app.route("/")
def start():
    """List all available routes."""
    return (
        f"Climate Analysis - Honolulu, Hawai<br/>"
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> <br/>" 
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of Precipitation Values."""

#Convert the query results to a Dictionary using date as the key and prcp as the value.
    #Query Precipitation values from 'measurement'

    session=Session(engine)
    prep_results = session.query(Measurement).all()

    #Ending session - ending communication with DB

    session.close()

    #create a dictionary with 'Date' as key and 'precipitation' as value
   
    #date_list = []
    #stn_list = []
    date_stn_dict = {}
    
    for measurement in prep_results:
        
        #date_list.append(measurement.date)
        #stn_list.append(measurement.prcp)
        #date_stn_dict = dict(zip(date_list,stn_list))

        # Adding a new key value pair to the dictionary
        
        date_stn_dict.update({measurement.date: measurement.prcp})
        
        

    return jsonify(date_stn_dict)

@app.route("/api/v1.0/stations")
def stations():
    """List of stations."""

    #Query for Station names from "station"

    session = Session(engine)
    stn_results = session.query(Station.name).all()

    #ending session 

    session.close()

    #convert list of tuples into list

    list_stn = list(np.ravel(stn_results))

    #Returning Json representation of results
   
    return (jsonify(list_stn))


@app.route("/api/v1.0/tobs")
def tobs():
    """List of Temp Obs and Dates."""

    #query for the dates and temperature observations from a year from the last data point.

    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    session.close()

    # converting the last_date value(string) to 'date' type
    lst_dt_2_date = dt.datetime.strptime(last_date[0],'%Y-%m-%d')

    # Calculate the date 1 year ago from the last data point in the database
    dt_last_yr = lst_dt_2_date - relativedelta(years=1)

    #covert the previous date to string format
    date_yr_b4_date = dt.datetime.strftime(dt_last_yr,"%Y-%m-%d")

    session = Session(engine)

    final_query = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date>= date_yr_b4_date).filter(Measurement.date <=last_date[0]).all()

    session.close()

    Date_Tob_list = []

    for measurement in final_query:
        date_tob_dict = {}
        date_tob_dict["Date"] = measurement.date
        date_tob_dict["Tobs"] = measurement.tobs
        Date_Tob_list.append(date_tob_dict)


    return(jsonify(Date_Tob_list))


#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.


#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.


#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/")
def dates_list_func():
    session = Session(engine)

    dates = session.query(Measurement.date).all()

    session.close()

    dates_list = list(np.ravel(dates))

    return jsonify(dates_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    keys_list = ["Minimun_Tob","Avg_Tob","Maximum_Tob"]

    search_date = start

    session = Session(engine)
    srt_query = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= search_date).all()
    session.close()
    srt_query_list = list(np.ravel(srt_query))

    dict_zip = dict(zip(keys_list,srt_query_list))
    return jsonify(dict_zip)

@app.route('/api/v1.0/<start>/<end>')
def srt_end_date(start,end):

    keys_list = ["Minimun_Tob","Avg_Tob","Maximum_Tob"]

    srt_date = start
    end_date = end

    session = Session(engine)
    srt_end_query = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= srt_date).filter(Measurement.date <= end_date).all()
    session.close()

    srt_end_q_list = list(np.ravel(srt_end_query))

    dict_zip = dict(zip(keys_list,srt_end_q_list))
    return jsonify(dict_zip)

if __name__ == '__main__':
    app.run(debug=True)




