# -*- coding: utf-8 -*-

"""

This is the final working code for DAQ Data aquiring.
The Database Feature is included in this code.

A few to do's before testing the code 

1. Please chande the MCS Address before testing the code as per you ip configuration. Variable used for this purpose is mcs_add

2. Please set the number of samples required to be aquired per channel in a single run

3. Please choose the run type i.e continuous aquiring or prompt aquiring.
   (a) Continuos type means the data gets aquired from all channels continuously without any user prompt.
   (b) Prompt type means the script runs for a time aquiring samples from all the seven channels, waits for the user input to start the next run and so on.

"""

# Importing the libraries
import ctypes
import numpy
import json
import requests

# Setting up
# Load the DLL
nidaq = ctypes.windll.nicaiu
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
DAQmx_Val_Cfg_Default = int32(-1)

# Fixing Some values. Constants
# Please do not change the values unless necessary
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0

# MCS IP Address
# Please change the IP Address as per the pc ip configuration
mcs_add = "192.168.43.225:8000"

# set the run type. Change the var to be equal to "prompt" for prompt run type.
run_type = "prompt"

# Routine to check error everytime the data is aquired
def CHK(err):

       if err < 0:

        buf_size = 10000
       
        buf = ctypes.create_string_buffer('\000' * buf_size)
       
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
       
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

#intitializing the variables
taskHandle = TaskHandle(0)

# Number of samples to be aquired per channel
# Please change the value as per requirement
max_num_samples = 2

# Reference to the seven DAQ analog channel ports which aquire the data
# Please do not change unless necessary
# If needed to aquire samples from specified multiple ports, change the elements of the  port array
port = ["Dev1/ai0", "Dev1/ai1", "Dev1/ai2", "Dev1/ai3", "Dev1/ai4", "Dev1/ai5", "Dev1/ai6"]

dummy_var = 1

while dummy_var == 1:
    
    print "\nNew Run Started\n"

    # port number
    i = 0;
    
    data_array = []    
    
    # loop to aquire the data from all the seven analog channel ports in a single run
    while(i < len(port)):

        # this variable stores the aquired data samples
        data = numpy.zeros((max_num_samples,),dtype=numpy.float64)
    
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))

        CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,port[i],
                                            "", DAQmx_Val_Cfg_Default, 
                                            float64(-10.0), float64(10.0), 
                                            DAQmx_Val_Volts, None))

        CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(10000.0),
                                         DAQmx_Val_Rising,DAQmx_Val_FiniteSamps, 
                                         uInt64(max_num_samples)));

        CHK(nidaq.DAQmxStartTask(taskHandle))

        read = int32()

        CHK(nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0), 
                                      DAQmx_Val_GroupByChannel,data.ctypes.data, 
                                      max_num_samples, ctypes.byref(read), None))

        # printing the aquired values
        print "Analog Port %d : Acquired %d points"%(i+1, read.value)
        print data
        print "\n"
        
        #aquired_Data_List = list(data)
        #print aquired_Data_List
        
        
        
        # MCS database connection
        # this block sends a request to the mcs database connection with a list of aquired data samples from all channels
        aquired_Data_List = list(data)
        
        # json_obj={str('channel'+str(i+1)):aquired_Data_List}
        data_array.append(aquired_Data_List)
        
        if taskHandle.value != 0:
            nidaq.DAQmxStopTask(taskHandle)
            nidaq.DAQmxClearTask(taskHandle)

        # incrementing the port number to move to the next available port
        i = i + 1

    json_object =  {
                        'channel1':data_array[0],
                        'channel2':data_array[1],
                        'channel3':data_array[2],
                        'channel4':data_array[3],
                        'channel5':data_array[4],
                        'channel6':data_array[5],
                        'channel7':data_array[6],
                    }
        
    headers = {'Content-type': 'application/json','Accept': 'text/plain'}
    r=requests.get("http://"+mcs_add+"/get_daq_data/", data=json.dumps(json_object), headers=headers)
    # print "\nNew Run Started\n"
    if run_type == "prompt":    
        print "All the data in this run aquired, press Enter key to start the next run"
        raw_input()
