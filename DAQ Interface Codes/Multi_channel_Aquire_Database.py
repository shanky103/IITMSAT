# -*- coding: utf-8 -*-

""""

This is the code for multiple channel DAQ Data aquiring in a single run.
The database feature has also been added to the code.
Please add the correct IP Address to the mcs_add variable.

"""


import ctypes
import numpy
import json
import requests

# load the DLL
nidaq = ctypes.windll.nicaiu
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348

# setting up the constants
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0

# MCS IP Address
# Please change the IP Address as per the pc ip configuration
mcs_add = "192.168.1.7:8000"

#routine to check error everytime
def CHK(err):

       if err < 0:

        buf_size = 10000

        buf = ctypes.create_string_buffer('\000' * buf_size)

        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)

        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

# intialising the variables
taskHandle = TaskHandle(0)

# Number of samples to be aquired per channel in a single run
max_num_samples = 5

# Reference to the seven DAQ analog channel ports which aquire the data
# Please do not change unless necessary
# If needed to aquire samples from specified multiple ports, change the elements of the  port array
port = ["Dev1/ai0", "Dev1/ai1", "Dev1/ai2", "Dev1/ai3", "Dev1/ai4", "Dev1/ai5", "Dev1/ai6"]

i = 0;

# loop to aquire data from all seven analog ports in a single run
while(i < len(port)):

    data = numpy.zeros((max_num_samples,),dtype=numpy.float64)
  
    CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))

    CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,port[i],"", 
                                        DAQmx_Val_Cfg_Default, float64(-10.0), 
                                        float64(10.0), DAQmx_Val_Volts, None))

    CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(10000.0), 
                                        DAQmx_Val_Rising,DAQmx_Val_FiniteSamps, 
                                        uInt64(max_num_samples)));

    CHK(nidaq.DAQmxStartTask(taskHandle))

    read = int32()

    CHK(nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0), 
                                    DAQmx_Val_GroupByChannel,data.ctypes.data, 
                                    max_num_samples, ctypes.byref(read), None))

    print "Analog Channel %d : Acquired %d points"%(i+1, read.value)

    #printing the aquired samples
    print data

    # MCS database connection
    # this block sends a request to the mcs database connection with a list of aquired data samples from all channels
    aquired_Data_List = list(data)
    
    json_obj={'channel':'ai0','aquired_Data_List':aquired_Data_List}

    headers = {'Content-type': 'application/json','Accept': 'text/plain'}

    r=requests.get("http://"+mcs_add+"/get_daq_data/", data=json.dumps(json_obj), headers=headers)
               
    
    if taskHandle.value != 0:
        nidaq.DAQmxStopTask(taskHandle)
        nidaq.DAQmxClearTask(taskHandle)

    #incrementing the port number to move to the next port    
    i = i + 1;

print "All the data aquired, press Enter key to quit"
raw_input()
