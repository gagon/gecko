import pandas as pd
import sys
import numpy as np
import csv
import os
import lasio
import datetime

def load_data(folder):

    raw_df=pd.DataFrame()

    i=0
    for file in os.listdir(folder):
        if file.endswith(".las"):
            print(file)
            las = lasio.read(os.path.join(folder,file))
            if i==0:
                raw_df=las.df()
            else:
                raw_df=raw_df.join(las.df())
            i+=1

    cols=raw_df.columns.tolist()
    cols.sort()

    raw_df=raw_df[cols]

    return raw_df


def get_attr_raw_data(raw_df,tformat):

    timestamps_str=raw_df.columns.tolist()
    depths=raw_df.index.tolist()

    timestamps=[]
    for t in timestamps_str:
        timestamps.append(datetime.datetime.strptime(str(t),tformat))

    dt=[]
    for i in range(len(timestamps)-1):
        dt.append((timestamps[i+1]-timestamps[i]).total_seconds()/60.0) # delta time in minutes

    hist,bin_edges=np.histogram(dt)

    data={
        "timestamps_str":timestamps_str,
        "timestamps_min":timestamps_str[0],
        "timestamps_max":timestamps_str[-1],
        "dt":dt,
        "dt_hist":hist.tolist(),
        "dt_bins":bin_edges.tolist(),
        "depths":depths,
        "depth_min":min(depths),
        "depth_max":max(depths),
        "depth_interval":depths[1]-depths[0],
        "trace_depth_count":len(depths)
    }

    return data


# df.to_csv("orig_data.csv",index=False)


def dts_fill_gaps(timestamps_str,raw_df,tformat):

    tol=0.1

    new_df=pd.DataFrame()
    new_timestamps=[]


    for i in range(len(timestamps_str)-1):
        curr_time=datetime.datetime.strptime(str(timestamps_str[i]),tformat)
        next_time=datetime.datetime.strptime(str(timestamps_str[i+1]),tformat)

        curr_trace=list(raw_df[timestamps_str[i]].values)

        new_df[timestamps_str[i]]=curr_trace
        new_timestamps.append(timestamps_str[i])

        dt_traces=(next_time-curr_time).total_seconds()

        if i==0:
            dt=dt_traces
            trace_len=len(curr_trace)

        if dt_traces>dt*(1.0+tol):

            new_time=curr_time

            while new_time+datetime.timedelta(seconds=dt)<next_time:

                new_time+=datetime.timedelta(seconds=dt)

                new_time_str=new_time.strftime(tformat)
                new_df[new_time_str]=np.zeros(trace_len)
                new_timestamps.append(new_time_str)

                # trace_idx=time_collection.index(time_collection[i])

    print(new_df.shape)

    return new_df,new_timestamps


def save_loaded_data(folder,df,timestamps,depths):

    df.to_csv(os.path.join(folder,"dts.csv"),index=False,header=False)

    with open(os.path.join(folder,'timestamps.txt'), 'w') as f:
        for item in timestamps:
            f.write("%s\n" % item)

    with open(os.path.join(folder,'depths.txt'), 'w') as f:
        for item in depths:
            f.write("%s\n" % item)

def calc_geothermal(folder,timestamps_str,df,start,end,tformat,depths):

    start_idx=0
    for t in timestamps_str:
        # print(datetime.datetime.strptime(start,"%Y-%m-%d %H:%M:%S"),datetime.datetime.strptime(t,tformat))
        if datetime.datetime.strptime(start,"%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(t,tformat):
            break
        start_idx+=1

    end_idx=0
    for t in timestamps_str:
        if datetime.datetime.strptime(end,"%Y-%m-%d %H:%M:%S")<datetime.datetime.strptime(t,tformat):
            break
        end_idx+=1


    df = df.replace({np.nan: 0})
    geothermal = df.iloc[:,start_idx:end_idx].mean(axis=1).values.tolist()

    trace={
        "temperature":geothermal,
        "depth":depths
    }

    # print(trace)
    return trace

def calc_norm_dts(geothermal_trace,dts_data):
    norm_dts_data=np.array((np.array(dts_data).T-np.array(geothermal_trace)).T).tolist()
    return norm_dts_data
