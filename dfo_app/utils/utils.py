import json
import os
import csv
import datetime
import numpy as np

# required for saving json files
dirname=os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) # added after restructuring files/folders

def get_session_json():
    json_fullpath=os.path.join(dirname,r"temp\session.json")
    if os.path.isfile(json_fullpath):
        data = json.load(open(json_fullpath))
    else:
        data={}
    return data


def save_session_json(session):
    json_fullpath=os.path.join(dirname,r"temp\session.json")
    json.dump(session, open(json_fullpath, 'w'),indent=4, sort_keys=True)
    return "None"


def read_txt(file,type):
    res=[]
    with open(file, newline='') as csvfile:
        s = csv.reader(csvfile, delimiter='\n')
        for row in s:
            if type=="float":
                res.append(float(row[0]))
            elif type=="geothermal":
                r=str(row[0]).split("\t")
                res.append([float(r[0]),float(r[1])])
            else:
                res.append(row[0])
    res=np.array(np.array(res).T).tolist()
    return res


def read_pt(file):
    res=[]
    with open(file, newline='') as csvfile:
        s = csv.reader(csvfile, delimiter='\n')
        for row in s:
            r=str(row[0]).split("\t")
            # print(r)
            # t=datetime.datetime.strptime(r[0],"%m/%d/%Y %I:%M")
            # t=t.strftime("%Y-%m-%d %H:%M:%S")
            res.append([r[0],float(r[1]),float(r[2])])
    res=np.array(np.array(res).T).tolist()
    return res

def convert_timestamps(timestamps,format1,format2,dhour):
    t_new=[]
    for t in timestamps:
        if dhour>=0:
            t=datetime.datetime.strptime(t,format1)+datetime.timedelta(hours=abs(dhour))
        else:
            t=datetime.datetime.strptime(t,format1)-datetime.timedelta(hours=abs(dhour))
        t_new.append(t.strftime(format2))
    return t_new


def depth_interp_traces(trace,depths):
    temps=np.interp(depths,trace[0],trace[1]).tolist()
    new_trace=[depths,temps]
    return new_trace


def dts_subs_geothermal(dts,geothermal_trace):
    new_dts=np.array((np.array(dts).T-np.array(geothermal_trace)).T).tolist()
    return new_dts


def calc_completion_rel_ids(table):
    ids=[]
    for comp in table:
        ids.append(float(comp["id"]))

    max_id=max(ids)
    rel_ids=(np.array(ids)/max_id*10.0).tolist() # 20 is max id in the completion plot
    max_rel_id=max(rel_ids)

    for i,comp in enumerate(table):
        if table[i]["type"]=="perforation":
            table[i]["rel_id"]=max_rel_id
        else:
            table[i]["rel_id"]=rel_ids[i]
    return table

def build_completion(table):
    templates=get_completion_templates()
    table=calc_completion_rel_ids(table)
    completion_fig=[]
    print(table)
    for comp in table:
        fig=templates["figure"][comp["type"]]
        fig["y0"]=float(comp["start"])
        fig["y1"]=float(comp["end"])
        fig["x0"]=10.0-comp["rel_id"] # completion plot with max 20 for ID, so 10 is mid point
        fig["x1"]=10.0+comp["rel_id"] # completion plot with max 20 for ID, so 10 is mid point
        completion_fig.append(fig)
    return completion_fig

def get_completion_templates():
    path=os.path.join(dirname,r"temp\completion_templates.json")
    templates=json.load(open(path))
    return templates

def get_completion():
    path=os.path.join(dirname,r"temp\completion.json")
    completion=json.load(open(path))
    return completion

def save_completion_json(completion):
    json_fullpath=os.path.join(dirname,r"temp\completion.json")
    json.dump(completion, open(json_fullpath, 'w'),indent=4, sort_keys=True)
    return "None"


def save_txt(session):
    with open(session["well_geothermal_fullpath"], 'w') as f:
        for i,item in enumerate(session["geothermal_trace"]["depth"]):
            row=[str(session["geothermal_trace"]["depth"][i]),str(session["geothermal_trace"]["temperature"][i])]
            f.write("%s\n" % "\t".join(row))
