import socket
import pyaudiowpatch as pyaudio
import time

fpb = 512
def start_sender(args, wasapi_def):
    global fpb
    ip, port = args
    print(ip, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def cb(in_data, frame_size, time_inf, status):
        sock.sendto(in_data, (ip, port))
        return (None, pyaudio.paContinue)

    pa = pyaudio.PyAudio()

    name = wasapi_def['name']
    istream = pa.open(input_device_index=wasapi_def['index'], 
                    rate=int(wasapi_def['defaultSampleRate']), 
                    channels=wasapi_def['maxInputChannels'], 
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=fpb,
                    stream_callback=cb)

    istream.start_stream()
    print(f'Initialized stream for device "{name}".')

    while True:
        time.sleep(1.0)


