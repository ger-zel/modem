import math
import matplotlib.pyplot as plt
import random
import numpy
import pylab

def rand_gen(n, low=0, high=3):
    x = numpy.zeros(n/2, dtype = 'uint8')
    for i in range(n/2):
        x[i] = random.randint(low,high)
        # x[i] = 0
    return x

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
            out.append(a)
    return out

def downsample(x ,k):
    out = []
    i = 0
    new_len = len(x) / k
    for j in range(new_len):
        i = i + k
        out.append(x[i])
        # i = i + k
    return out

class raised_cosine():
    def __init__(self, n = 16, betta = 0.5):
        x = numpy.linspace(-20, 20, n)
        sinc = numpy.sinc(x)
        self.h = numpy.zeros(n)
        for i in range(n-1):
            self.h[i] = sinc[i] \
                * math.cos(math.pi * betta * i / n) \
                * 1 / (1 - 4 * pow(betta, 2) * pow(i, 2) / pow(n, 2))
    def apply_filter_complex(self, signal):
        i = numpy.real(signal)
        q = numpy.imag(signal)
        out_i = numpy.convolve(i, self.h)
        out_q = numpy.convolve(q, self.h)
        out = numpy.vectorize(complex)(out_i, out_q)
        return out
    def apply_filter(self, signal):
        out = numpy.convolve(signal, self.h)
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

def show_spectrum(signal):
    Pxx, freqs, t, plot = pylab.specgram(
        signal,
        NFFT=128, 
        Fs=8000, 
        detrend=pylab.detrend_none,
        window=pylab.window_hanning,
        noverlap=int(128 * 0.5))
    
    pylab.show()    

def modulate(x, Fcarr, Fsampl):
    qam = mapper_qam4()
    f = raised_cosine(n = 512)
    signal = qam.map_array(x)
    show_spectrum(signal)
    signal = upsample(signal, 16)
    show_spectrum(signal)
    # plt.plot(signal)
    signal = f.apply_filter(signal)
    show_spectrum(signal)
    # plt.plot(signal)
    signal = modulate_to_real(signal, Fcarr, Fsampl)
    show_spectrum(signal)
    return signal

def demodulate(signal, Fcarr, Fsampl):
    f = raised_cosine(n = 512)

    I = demod_from_real_to_I(signal, Fcarr, Fsampl)
    Q = demod_from_real_to_Q(signal, Fcarr, Fsampl)
    I = f.apply_filter(I)
    Q = f.apply_filter(Q)
    S = numpy.vectorize(complex)(I, Q)
    # plt.plot(S)
    # plt.show()
    show_spectrum(S)
    # S = S[512:]
    S = downsample(S, 16)
    show_spectrum(S)
    data = slice_signal(S)
    return data

if __name__ == '__main__':
    x = rand_gen(1024)
    Fcarr = 2000
    Fsampl = 8000
    signal = modulate(x, Fcarr, Fsampl)
    y = demodulate(signal, Fcarr, Fsampl)
    print x
    print y
