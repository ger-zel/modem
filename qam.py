import math
import matplotlib.pyplot as plt
import random
import numpy
import pylab
import filter
import utils
import operator

class mapper_qam4:
    def __init__(self):
        self.I = []
        self.Q = []
        alpha = [225, 135, 315, 45]
        for i in range(len(alpha)):
            self.I.append(math.cos(alpha[i] * math.pi / 180))
            self.Q.append(math.sin(alpha[i] * math.pi / 180))
    def map_i(self, x):
        return self.I[int(x)]
    def map_q(self, x):
        return self.Q[int(x)]
    def map_array(self, x):
        out = []
        for n in range(len(x)):
            i = self.map_i(x[n])
            q = self.map_q(x[n])
            out.append(complex(i,q))
        return out

def slice_signal(signal):
    I = numpy.real(signal)
    Q = numpy.imag(signal)
    out = []
    for i in range(len(signal)):
        if I[i] >= 0 and Q[i] >= 0:
            out.append(3)
        if I[i] >= 0 and Q[i] < 0:
            out.append(2)
        if I[i] < 0 and Q[i] >= 0:
            out.append(1)
        if I[i] < 0 and Q[i] < 0:
            out.append(0)
    return out

def upsample(x, k):
    out = []
    for a in x:
        out.append(a)
        for i in range(k-1):
            # out.append(a)
            out.append(0)
    return out

def downsample(x ,k):
    out = []
    i = 0
    new_len = len(x) / k
    for j in range(new_len):
        # i = i + k
        out.append(x[i])
        i = i + k
    return out

def modulate_to_real(signal, Fc, Fs):
    out = []
    for i in range(len(signal) - 1):
        s = numpy.real(signal[i]) * math.cos(2 * Fc * math.pi * i / Fs) \
            + numpy.imag(signal[i] * math.sin(2 * Fc * math.pi * i/ Fs))
        out.append(s)
    return out

def demod_from_real_to_I(signal, Fc, Fs):
    out = []
    for i in range(len(signal) - 1):
        s = numpy.cos(2 * Fc * math.pi * i / Fs) * signal[i]
        out.append(s)
    return out

def demod_from_real_to_Q(signal, Fc, Fs):
    out = []
    for i in range(len(signal) - 1):
        s = numpy.sin(2 * Fc * math.pi * i/ Fs) * signal[i]
        out.append(s)
    return out

def modulate(x, Fcarr, Fsampl, K):
    qam = mapper_qam4()
    # f = filter.raised_cosine(n=256)
    f = filter.low_pass(Fcutt = Fsampl/K)
    signal = qam.map_array(x)
    # utils.show_spectrum(signal)
    signal = upsample(signal, K)
    # utils.show_spectrum(signal)
    signal = f.apply_complex(signal)
    utils.show_spectrum(signal)
    signal = modulate_to_real(signal, Fcarr, Fsampl)
    utils.show_spectrum(signal)
    return signal

def demodulate(signal, Fcarr, Fsampl, K):
    # f = filter.raised_cosine(n=256)
    f = filter.low_pass(Fcutt = Fsampl/K)
    I = demod_from_real_to_I(signal, Fcarr, Fsampl)
    Q = demod_from_real_to_Q(signal, Fcarr, Fsampl)
    I = f.apply_real(I)
    Q = f.apply_real(Q)
    S = numpy.vectorize(complex)(I, Q)
    # utils.show_spectrum(S)
    S = downsample(S, K)
    # utils.show_spectrum(S)
    data = slice_signal(S)
    return data

if __name__ == '__main__':
    x = utils.rand_gen(1024)
    Fcarr = 2000
    Fsampl = 8000
    K = 4
    signal = modulate(x, Fcarr, Fsampl, K)
    print len(signal)
    y = demodulate(signal, Fcarr, Fsampl, K)
    x = x.tolist()

    print x
    print y

    print len(x)
    print len(y)

    if bool(utils.contains(x[0:196], y)) == False:
        print "data error"
    else:
        print "data ok"
