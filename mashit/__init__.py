
import numpy as np
from scikits.audiolab import Sndfile, play as al_play

class Snip(object):
    def __init__(self, filename_or_matrix, samplerate=None):
        if isinstance(filename_or_matrix, basestring):
            filename = filename_or_matrix
            if filename.endswith('mp3'):
                filename = '%s.wav' % filename[:-4]
                pass # TODO convert to wav and then fall through
            assert filename.endswith('wav')
            
            f = Sndfile(filename, 'r')
            self.samplerate = f.samplerate
            self.matrix = f.read_frames(f.nframes)
            f.close()
            
        elif isinstance(filename_or_matrix, (np.matrix, np.ndarray)):
            assert samplerate is not None
            self.samplerate = samplerate
            self.matrix = filename_or_matrix

        self.length = self.matrix.shape[0] / float(self.samplerate)
    
    def play(self, samplerate=None):
        """
        Audiolab expects a matrix with one column per frame,
        hence the transpose.
        """
        al_play(self.matrix.T, samplerate or self.samplerate)

    def __call__(self, start, end=None):
        """
        Because __getslice__ only accepts integer slices,
        we use the call syntax.

        Not sure why, but numpy matrices allow non-integer slices.
        TODO: switch back to slice syntax s[:8.2] instead of call s(8.2)
        """
        if end is None:
            end = start
            start = 0
            
        start_frame = start * self.samplerate
        end_frame = end * self.samplerate
        new_matrix = self.matrix[start_frame:end_frame]
        
        return Snip(new_matrix, self.samplerate)
    

    def __add__(self, other):
        assert self.samplerate == other.samplerate # for now
        new_matrix = np.append(self.matrix, other.matrix, axis=0)
        return Snip(new_matrix, self.samplerate)
    
    def loop(self, n):
        # TODO: do this with Kronecker products
        new_snip = self
        for i in range(n-1):
            new_snip = new_snip + self
        return new_snip

    __mul__ = loop # alias

    def fadein(self, length):
        """
        For now let's try linear.
        """
        intro_frames = length*self.samplerate
        # goes from 0 to 1 in :length: seconds
        start_vol = np.arange(0, length, 1 / float(intro_frames))
        
        remaining_frames = self.matrix.shape[0] - len(start_vol)
        remaining_vol = np.array([1] * remaining_frames)

        volume = np.append(start_vol, remaining_vol)

        assert len(volume) == self.matrix.shape[0]

        # Not done yet.
