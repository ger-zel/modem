import math
import numpy

class raised_cosine:
    def __init__(self, n = 16, betta = 0.5):
        x = numpy.linspace(-20, 20, n)
        sinc = numpy.sinc(x)
        self.h = numpy.zeros(n)
        for i in range(n-1):
            self.h[i] = sinc[i] \
                * math.cos(math.pi * betta * i / n) \
                * 1 / (1 - 4 * pow(betta, 2) * pow(i, 2) / pow(n, 2))
    def apply_complex(self, signal):
        i = numpy.real(signal)
        q = numpy.imag(signal)
        out_i = numpy.convolve(i, self.h)
        out_q = numpy.convolve(q, self.h)
        out = numpy.vectorize(complex)(out_i, out_q)
        return out
    def apply_real(self, signal):
        out = numpy.convolve(signal, self.h)
        return out
