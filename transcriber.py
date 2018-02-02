from pocketsphinx import AudioFile, get_model_path
import subprocess
import glob
import speech_recognition as sr
import json
from os import path, remove, devnull
import shlex
import math

__FNULL__ = open(devnull, 'w')
__MODEL_PATH__ = get_model_path()

def get_audio_name(fname):
    return path.splitext(fname)[0] + ".wav"


def convert_to_wav(fname):
    ofname = get_audio_name(fname)
    if path.isfile(ofname):
        remove(ofname)
    command = "ffmpeg -y -i {0} -ab 160k -ac 2 -ar 44100 -vn {1}".format(fname, ofname)
    subprocess.call(shlex.split(command), stderr=__FNULL__, stdout=__FNULL__)
    return True if path.isfile(ofname) else False


def process_file(afname, offset=0, secs_interval=10):
    r = sr.Recognizer()
    result = []
    starting_offset = (offset / secs_interval)
    with sr.WavFile(afname) as source:
        end_offset = int(math.ceil(float(source.DURATION) / float(secs_interval)))
        for i in xrange(starting_offset, end_offset):
            print "Processing TimeFrame #%s to TimeFrame #%s" % (i * secs_interval, (i + 1) * secs_interval - 1)
            audio = r.record(source, duration=secs_interval-1, offset=i * secs_interval)
            try:
                result.append([r.recognize_sphinx(audio), i * secs_interval, (i + 1) * secs_interval - 1])
            except Exception as ex:
                continue
    return result

if __name__ == '__main__':
    files = glob.glob("data/*.mp4")

    for file in files:
        conversion = convert_to_wav(file)
        if not conversion:
            print "File %s can't be processed!" % file
            continue
        print "File :" + file + " converted: " + ("OK" if conversion else "KO")
        afname = get_audio_name(file)
        result = process_file(afname=afname, offset=0, secs_interval=20)
        transcription_name = "processed/" + path.basename(file).split(".")[0] + ".json"
        json.dump(result, fp=open(transcription_name, "w"), sort_keys=True, indent=3)

