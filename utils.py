import math 
import matplotlib.pyplot as ply
import random
import numpy
import pylab
import struct

def rand_gen(n, low=0, high=3):
    x = numpy.zeros(n/2, dtype = 'uint8')
    for i in range(n/2):
        x[i] = random.randint(low,high)
        # x[i] = 0
    return x

def show_spectrum(signal, Fsample = 8000):
    Pxx, freqs, t, plot = pylab.specgram(
        signal,
        NFFT=128, 
        Fs = Fsample, 
        detrend=pylab.detrend_none,
        window=pylab.window_hanning,
        noverlap=int(128 * 0.5))
    
    pylab.show()    

def list_find(what, where):
    if not what: # empty list is always found
        return 0
    try:
        index = 0
        while True:
            index = where.index(what[0], index)
            if where[index:index+len(what)] == what:
                return index # found
            index += 1 # try next position
    except ValueError:
        return -1 # not found

def contains(what, where):
    i = list_find(what, where)
    return [i, i + len(what)] if i >= 0 else [] #NOTE: bool([]) == False

def conv_to_audio(signal):
    '''We use L16_SE format!'''
    fmt = "<%dh" % len(signal)
    const = 0x4000
    data = [numpy.int16(const * x) for x in signal]
    out = struct.pack(fmt, *data)
    return out

def conv_from_audio(signal, n):
    '''We use L16_SE format!'''
    fmt = "<%dh" % n
    const = 0x4000
    data = [numpy.int16(float(x) / const) for x in signal]
    out = list(struct.unpack(fmt, data))
    return out

def chunk(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


