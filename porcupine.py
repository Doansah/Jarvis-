from abc import ABC, abstractmethod
from time import time



'''
The first layer which identifies the wakeword, 
from esp32: 
1) Tells hardware to start recording..
2) For how long 

'''
class wakeController(): 
    @abstractmethod
    def startRecording(): 
        pass 
    @abstractmethod
    def stopRecording():
        pass 

class Porcupine(wakeController): 
    def startRecording():
        # INDICATE THAT audio device is listening (turn on led light) 
        # Send http request... 
        # Pass on recording to whisperAPI...






