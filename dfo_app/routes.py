from dfo_app import app
from flask import render_template
from flask_socketio import SocketIO, send, emit,disconnect
import numpy as np
import json
from dfo_app.utils import utils
from dfo_app.utils import load_data as ld
import pandas as pd
import datetime
import os
import shutil


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # for js files not being cached
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

tformat_standard="%Y-%m-%d %H:%M:%S"

# dirname=os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
dirname=os.path.abspath(os.path.dirname( __file__ ))

@app.route('/')
@app.route('/index')
def index():
    page_active={"setup":"active"}

    session=utils.get_session_json()

    return render_template('index.html',page_active=page_active,session=session)


@app.route('/integrated_plot')
def integrated_plot_page():
    page_active={"integrated_plot":"active"}
    return render_template('integrated_plot.html',page_active=page_active)


@app.route('/integrated_plot_plot1')
def integrated_plot_page1():
    page_active={"integrated_plot":"active"}

    session=utils.get_session_json()

    if session["integrated_plot_data"]=="DTS":
        dts_folder=session["output_dts_folder"]
    else:
        dts_folder=session["norm_dts_folder"]

    df = pd.read_csv(os.path.join(dts_folder,"dts.csv"),header=None)
    df = df.replace({np.nan: 0})
    dts_data=df.values.tolist()
    session["dts_data"]=dts_data

    session["completion"]=json.load(open(os.path.join(dirname,r"temp\completion.json")))["figure"]

    depths=utils.read_txt(os.path.join(dts_folder,"depths.txt"),"float")
    session["dts_depths"]=depths


    timestamps=utils.read_txt(os.path.join(dts_folder,"timestamps.txt"),"string")
    timestamps=utils.convert_timestamps(timestamps,session["tformat"],tformat_standard,session["dts_hour_shift"])
    session["dts_timestamps"]=timestamps

    session["date_min"]=min(timestamps)
    session["date_max"]=max(timestamps)


    if session["well_geothermal_fullpath"]:
        geothermal=utils.read_txt(session["well_geothermal_fullpath"],"geothermal")
        session["geothermal"]=geothermal
    else:
        session["geothermal"]=[[],[]] # fill empty lists

    if session["well_inclination_fullpath"]:
        inclination=utils.read_txt(session["well_inclination_fullpath"],"geothermal")
        session["inclination"]=inclination
    else:
        session["inclination"]=[[],[]] # fill empty lists

    if session["downhole_data_fullpath"]:
        pt=utils.read_pt(session["downhole_data_fullpath"])
        session["pt"]=pt
    else:
        session["pt"]=[[],[],[]] # fill empty lists

    uom={
        "temp_unit":session["temp_unit"],
        "pres_unit":session["pres_unit"]
    }

    return render_template('integrated_plot_plot1.html',page_active=page_active,session=session,uom=uom)

@app.route('/completion')
def completion_builder_page():
    page_active={"completion":"active"}
    session=utils.get_session_json()
    completion_templates=utils.get_completion_templates()
    completion=utils.get_completion()
    return render_template('completion_builder.html',
                            page_active=page_active,
                            session=session,
                            completion_templates=completion_templates,
                            completion=completion)


@app.route('/load_data')
def load_data_page():
    page_active={"load_data":"active"}
    session=utils.get_session_json()
    # completion_templates=utils.get_completion_templates()
    # completion=utils.get_completion()
    return render_template('load_data.html',
                            page_active=page_active,
                            session=session,
                            # completion_templates=completion_templates,
                            # completion=completion
                            )

@app.route('/geothermal')
def geothermal_page():
    page_active={"geothermal":"active"}
    session=utils.get_session_json()
    # completion_templates=utils.get_completion_templates()
    # completion=utils.get_completion()
    return render_template('geothermal.html',
                            page_active=page_active,
                            session=session,
                            # completion_templates=completion_templates,
                            # completion=completion
                            )


@app.route('/config_plot')
def config_plot():
    page_active={"integrated_plot":"active"}
    page_setup={"dashboad_num":5,"plot_num":6}
    json_fullpath=os.path.join(dirname,r"temp\config_plot.json")
    config_plot = json.load(open(json_fullpath))
    return render_template('config_plot.html',page_active=page_active,page_setup=page_setup,config_plot=config_plot)

@app.route('/calibration')
def calibration_page():
    page_active={"calibration":"active"}
    return render_template('calibration.html',page_active=page_active)


@app.route('/processing')
def processing_page():
    page_active={"processing":"active"}
    return render_template('processing.html',page_active=page_active)



@socketio.on('save_session')
def save_session(session):
    utils.save_session_json(session)
    print("hi hi")
    emit("saved")
    return "None"

@socketio.on('save_ranges')
def save_configs(configs):
    session=utils.get_session_json()
    session["zmin"]=configs["zrange"][0]
    session["zmax"]=configs["zrange"][1]
    session["temp_range"]=configs["temp_range"]
    session["pres_range"]=configs["pres_range"]
    session["colormap"]=configs["colormap"]
    utils.save_session_json(session)
    emit("saved")
    return "None"

@socketio.on('save_completion')
def save_completion(completion_table):
    completion_fig=utils.build_completion(completion_table)
    completion_json={
        "figure":completion_fig,
        "table":completion_table
    }
    utils.save_completion_json(completion_json)
    return "None"

@socketio.on('load_data')
def load_data(raw_folder,out_folder):
    session=utils.get_session_json()
    raw_df=ld.load_data(raw_folder)
    data=ld.get_attr_raw_data(raw_df,session["tformat"])
    new_df,new_timestamps=ld.dts_fill_gaps(data["timestamps_str"],raw_df,session["tformat"])
    ld.save_loaded_data(out_folder,new_df,new_timestamps,data["depths"])
    emit("raw_data_loaded",data)

    return "None"

@socketio.on('calc_geothermal')
def calc_geothermal(start,end):
    session=utils.get_session_json()
    dts_folder=session["output_dts_folder"]
    df = pd.read_csv(os.path.join(dts_folder,"dts.csv"),header=None)
    timestamps_str=utils.read_txt(os.path.join(dts_folder,"timestamps.txt"),"string")
    depths=utils.read_txt(os.path.join(dts_folder,"depths.txt"),"float")
    data=ld.calc_geothermal(dts_folder,timestamps_str,df,start,end,session["tformat"],depths)

    emit("plot_geothermal",data)

    return "None"

@socketio.on('save_geothermal')
def save_geothermal(session):

    depths=utils.save_txt(session)

    emit("geothermal_saved")

    return "None"


@socketio.on('calc_norm_dts')
def calc_norm_dts():

    session=utils.get_session_json()
    geothermal=utils.read_txt(session["well_geothermal_fullpath"],"geothermal")

    dts_folder=session["output_dts_folder"]
    df = pd.read_csv(os.path.join(dts_folder,"dts.csv"),header=None)
    df = df.replace({np.nan: 0})
    dts_data=df.values.tolist()

    norm_dts_data=ld.calc_norm_dts(geothermal[1],dts_data)

    new_df=pd.DataFrame(norm_dts_data)

    new_df.to_csv(os.path.join(session["norm_dts_folder"],"dts.csv"),index=False,header=False)

    source=os.path.join(session["output_dts_folder"],"depths.txt")
    destination=os.path.join(session["norm_dts_folder"],"depths.txt")
    shutil.copytree(source, destination, dirs_exist_ok=True)

    source=os.path.join(session["output_dts_folder"],"timestamps.txt")
    destination=os.path.join(session["norm_dts_folder"],"timestamps.txt")
    shutil.copytree(source, destination, dirs_exist_ok=True)

    # df.to_csv(os.path.join(session["norm_dts_folder"],"dts.csv"),index=False,header=False)

    emit("geothermal_saved")

    return "None"
