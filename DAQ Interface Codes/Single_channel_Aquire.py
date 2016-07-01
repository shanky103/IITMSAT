# -*- coding: utf-8 -*-

"""

This is the code for single channel for DAQ Data aquiring.
The channel from which the data has to be aquired has to be specified.

"""

import ctypes
import numpy

# load the dll
nidaq = ctypes.windll.nicaiu 

int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32

# specifying the constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0

# Routine for checking the error
def CHK(err):

    if err < 0:

        buf_size = 100

        buf = ctypes.create_string_buffer('\000' * buf_size)

        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)

        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

# initializing the variables
taskHandle = TaskHandle(0)

# Number of samples to be aquired per channel
# Please change the value as per requirement
max_num_samples = 5

# the variable data stores the sample values
data = numpy.zeros((max_num_samples,),dtype=numpy.float64)

CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))

CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai0","",
                                   DAQmx_Val_Cfg_Default,
                                   float64(-10.0),float64(10.0),
                                   DAQmx_Val_Volts,None))

CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(10000.0),
                                DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                uInt64(max_num_samples)));

CHK(nidaq.DAQmxStartTask(taskHandle))

read = int32()

CHK(nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0),
                             DAQmx_Val_GroupByChannel,data.ctypes.data,
                             max_num_samples,ctypes.byref(read),None))

print "Analog Port : Acquired %d points"%(read.value)

# printing the aquired values
print data

if taskHandle.value != 0:
    nidaq.DAQmxStopTask(taskHandle)
    nidaq.DAQmxClearTask(taskHandle)

print "End of the sample aquiring process, press Enter key to quit"
raw_input()
