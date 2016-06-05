# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import ctypes
import numpy
import json
import requests
nidaq = ctypes.windll.nicaiu # load the DLL
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0
mcs_add = "192.168.1.7:8000"
#routine to check error everytime
def CHK(err):
       if err < 0:
        buf_size = 10000
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

taskHandle = TaskHandle(0)
max_num_samples = 2
port = ["Dev1/ai0", "Dev1/ai1", "Dev1/ai2", "Dev1/ai3", "Dev1/ai4", "Dev1/ai5", "Dev1/ai6"]
i = 0;
while(i < len(port)):
    data = numpy.zeros((max_num_samples,),dtype=numpy.float64)
  
    CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))
    CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,port[i],"", DAQmx_Val_Cfg_Default, float64(-10.0), float64(10.0), DAQmx_Val_Volts, None))
    CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(10000.0), DAQmx_Val_Rising,DAQmx_Val_FiniteSamps, uInt64(max_num_samples)));
    CHK(nidaq.DAQmxStartTask(taskHandle))
    read = int32()
    CHK(nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0), DAQmx_Val_GroupByChannel,data.ctypes.data, max_num_samples, ctypes.byref(read), None))
    print "Acquired %d points"%(read.value)
    mylist = list(data)
    print data
    json_obj={'channel':'ai0','mylist':mylist}
    headers = {'Content-type': 'application/json','Accept': 'text/plain'}
    r=requests.get("http://"+mcs_add+"/get_daq_data/", data=json.dumps(json_obj), headers=headers)
    
    if taskHandle.value != 0:
        nidaq.DAQmxStopTask(taskHandle)
        nidaq.DAQmxClearTask(taskHandle)
    i = i + 1;
print "All the data aquired, press Enter key to quit"
raw_input()
