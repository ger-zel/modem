import threading
import struct
import Queue
import alsaaudio
import time
import numpy

class Play(threading.Thread):
    def __init__(self, queue, channels=2, rate=8000, format=alsaaudio.PCM_FORMAT_S16_LE, periodsize=1024):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.q = queue
        self.end = False
        self.ready = False
        self.out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, 
                                 alsaaudio.PCM_NORMAL)
        self.out.setchannels(channels)
        self.out.setrate(rate)
        self.out.setformat(format)
        self.out.setperiodsize(periodsize)
    def samples_ready(self): # preload some buffers before start
        self.ready = True
    def done(self):
        self.end = True
    def run(self):
        cnt = 0
        while self.q.qsize() < 3:
            if cnt < 100:
                time.sleep(0.1)
                cnt = cnt + 1
            else:
                print "Man give some data to start with!"
                return
        self.ready = True
        while True:
            if self.ready == True:
                data = self.q.get()
                self.out.write(data)
                cnt = 0
                if self.q.qsize() < 1:
                    self.ready = False
            else:
                if cnt > 100:
                    break
                else:
                    cnt = cnt + 1
                    time.sleep(0.1) # use period size to calculate delay
            if self.end == True:
                while self.q.empty() == False:
                    data = self.q.get()
                    self.out.write(data)
                break

class Capture(threading.Thread):
    def __init__(self, queue, channel=2, rate=8000, format=alsaaudio.PCM_FORMAT_S16_LE, periodsize=1024):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.q = queue
        self.ready = False
        self.end = False
        self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 
                                 alsaaudio.PCM_NORMAL)
        self.inp.setchannels(channel)
        self.inp.setrate(rate)
        self.inp.setformat(format)
        self.inp.setperiodsize(periodsize)
    def wait_for_samples(self):
        cnt = 0
        self.ready = False
        while self.ready == False:
            cnt = cnt + 1
            time.sleep(0.1)
            if cnt == 100:
                break
        if self.ready == True:
            return True
        else:
            return False
    def done(self):
        self.end = True
    def run(self):
        while True:
            l,data = self.inp.read()
            self.q.put(data)
            self.ready = True
            if self.end == True:
                break

if __name__ == '__main__':

    class Echo:
        def __init__(self, buf_len):
            self.m = 2048       # echo delay
            self.len = buf_len
            self.delayed = [0]*(self.m + buf_len)
            self.alpha = 0.5
            self.fmt = "<%dh" % (self.len)
            self.out = ''
            self.out.zfill(self.len)
        def do_echo(self, input):
            x = list(struct.unpack(self.fmt,input))
            y = [0]*self.len
            for i in range(self.len):
                y[i] = int(x[i] + self.alpha * self.delayed[i])
                self.delayed[i + self.m] = y[i]
            self.delayed[0:self.m] = self.delayed[(len(self.delayed)-self.m):]
            self.out = struct.pack(self.fmt, *y)
            return self.out

    class Vocoder:
        def __init__(self, buf_len):
            self.len = buf_len
            self.fmt = "<%dh" % (self.len)
            self.compress_size = 0.6
            self.gap = 4        # 2 mult size!!
            self.out = ''
            self.out.zfill(self.len)

        def fill_with_gap(self, input):
            if self.gap == 0:
                x = input[:]
            else:
                x = [0] * int(len(input)/self.gap)
                x = input[0:len(input)-1:self.gap]
            return x

        def remove_center(self, inp, size_percent):
            n = len(inp)
            n_rem = int(n * size_percent/2)

            x = inp

            for i in range((n/2 - n_rem), (1+n/2 + n_rem)):
                x[i] = 0

            return x

        def do_vocode(self, input):
            inp = list(struct.unpack(self.fmt, input))
            inp_len = len(inp)

            x = self.fill_with_gap(inp)

            N = len(x)

            X = numpy.fft.fft(x)

            X = self.remove_center(X, self.compress_size)

            Y = [0] * inp_len

            Y[0:(N/2)] = (inp_len/N)*X[0:(N/2)]
            Y[(inp_len - N/2 + 1):inp_len-1] = (inp_len/N)*X[(1 + N/2):N-1]

            y = numpy.fft.ifft(Y)

            self.out = struct.pack(self.fmt, *y)
            return self.out

    import struct

    cnt = 0

    q_in = Queue.Queue()
    q_out = Queue.Queue()

    size = 256

    c = Capture(periodsize = size, queue = q_in)
    # c = Capture(periodsize = size, queue = q_in, rate=11000)
    c.start()

    p = Play(periodsize = size, queue = q_out)
    # p = Play(periodsize = size, queue = q_out, rate=11000)
    p.start()
    
    data = q_in.get()

    e = Echo(size * 2)
    v = Vocoder(size * 2)
    # data_out = e.do_echo(data)
    data_out = v.do_vocode(data)
    q_out.put(data_out)

    while True:
        data = q_in.get()
        # data_out = e.do_echo(data)
        data_out = v.do_vocode(data)
        q_out.put(data_out)
        p.samples_ready()
        cnt = cnt + 1
        if cnt > 1000:
            c.done()
            p.done()
            p.join()
            c.join()
            break
