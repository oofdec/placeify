import sounddevice as sd
import soundfile as sf
import numpy as np

import threading
import customtkinter as ctk
root = ctk.CTk(fg_color="black")
root.geometry(f"{root.winfo_screenwidth()}x500-10+{root.winfo_screenheight()-550}")
root.overrideredirect(True)

root.attributes("-topmost",True)
root.attributes("-transparentcolor","black")

TOTAL_SEGMENTS = 23
segmentwidth = 1/TOTAL_SEGMENTS
global bar_values
bar_values = []

visualizer_bars = []
def create_visualizers(segments):
    visualizer_bars.clear()

    for i in range(segments):
        segment = ctk.CTkFrame(root,width=35,height=15)

        visualizer_bars.append(segment)

def update_visualizers():
    bottom = root.winfo_height()

    if len(bar_values) == len(visualizer_bars):
        for i in range(len(bar_values)):
            segment = visualizer_bars[i]
            height=bar_values[i]*8

            segment.configure(height=height)
            segment.place(relx=i/TOTAL_SEGMENTS,relwidth=segmentwidth,y=bottom-height)
    root.update()
    root.after(58,update_visualizers)

def callback(outdata, frames, time, status):
    global idx
    global bar_values

    chunk = data[idx:idx+frames]
    idx += frames

    if len(chunk) < frames:
        outdata[:] = np.zeros((frames, data.shape[1]))
        return

    outdata[:] = chunk

    mono = chunk.mean(axis=1)
    fft = np.abs(np.fft.rfft(mono))
    bars = np.array_split(fft, TOTAL_SEGMENTS)

    bar_values = [np.mean(b) for b in bars]


create_visualizers(TOTAL_SEGMENTS)
root.after(0,update_visualizers) #kickstart loop

data, samplerate = sf.read("SONG HERE")
idx = 0

def sounddata_manager():
    with sd.OutputStream(callback=callback, samplerate=samplerate, channels=data.shape[1]):
        sd.sleep(int(len(data) / samplerate * 1000))


threading.Thread(target=sounddata_manager).start()
root.mainloop()
