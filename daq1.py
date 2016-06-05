import ctypes
import numpy
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
##############################

# initialize variables
taskHandle = TaskHandle(0)
max_num_samples = 10000000
data = numpy.zeros((max_num_samples,),dtype=numpy.float64)
nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle))
nidaq.DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai0:3","",
                                   DAQmx_Val_Cfg_Default,
                                   float64(-10.0),float64(10.0),
                                   DAQmx_Val_Volts,None)
nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(10000.0),
                                DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                uInt64(max_num_samples));
nidaq.DAQmxStartTask(taskHandle)
read = int32()
nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0),
                             DAQmx_Val_GroupByChannel,data.ctypes.data,
                             max_num_samples,(read),None)
print "Acquired %d points"%(read.value)
print data
if taskHandle.value != 0:
    nidaq.DAQmxStopTask(taskHandle)
    nidaq.DAQmxClearTask(taskHandle)
print "End of program, press Enter key to quit"
raw_input()
