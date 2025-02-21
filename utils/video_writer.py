import cv2
import numpy as np

class VideoWriter:
    def __init__(self, output_path, frame_rate = 30):
        
        self.output_path = output_path
        self.frame_rate = frame_rate
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self.writer = None
        self.recorder = None

    def record(self, frame):
        if self.recorder == None:
            ### Recorder ###

            frame_shape = np.shape(frame)
            frame_width = frame_shape[1]
            frame_height = frame_shape[0]

            # Create VideoWriter object to save the video
            self.recorder = cv2.VideoWriter(self.output_path + '.avi', self.fourcc, self.frame_rate, (frame_width, frame_height))
        
        self.recorder.write(frame)