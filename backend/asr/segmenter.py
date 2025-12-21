import numpy as np

class Segmenter:
    """
    Simple frame buffer for speech segments.
    Combines consecutive speech frames into a single segment.
    """
    def __init__(self):
        self.buffer = []

    def append_frame(self, frame: np.ndarray, is_speech: bool):
        if is_speech:
            self.buffer.append(frame)
        elif self.buffer:
            # Return concatenated speech frames
            segment = np.concatenate(self.buffer)
            self.buffer = []
            return segment
        return None

    def force_flush(self):
        if self.buffer:
            segment = np.concatenate(self.buffer)
            self.buffer = []
            return segment
        return None
