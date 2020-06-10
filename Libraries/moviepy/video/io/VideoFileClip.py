import os
import threading
import time

import numpy as np

import pygame as pg

from Libraries.moviepy.decorators import convert_masks_to_RGB, requires_duration
from Libraries.moviepy.tools import cvsecs

from Libraries.moviepy.audio.io.AudioFileClip import AudioFileClip
from Libraries.moviepy.Clip import Clip
from Libraries.moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader
from Libraries.moviepy.video.VideoClip import VideoClip


class VideoFileClip(VideoClip):

    """

    A video clip originating from a movie file. For instance: ::

        >>> clip = VideoFileClip("myHolidays.mp4")
        >>> clip.close()
        >>> with VideoFileClip("myMaskVideo.avi") as clip2:
        >>>    pass  # Implicit close called by context manager.


    Parameters
    ------------

    filename:
      The name of the video file. It can have any extension supported
      by ffmpeg: .ogv, .mp4, .mpeg, .avi, .mov etc.

    has_mask:
      Set this to 'True' if there is a mask included in the videofile.
      Video files rarely contain masks, but some video codecs enable
      that. For istance if you have a MoviePy VideoClip with a mask you
      can save it to a videofile with a mask. (see also
      ``VideoClip.write_videofile`` for more details).

    audio:
      Set to `False` if the clip doesn't have any audio or if you do not
      wish to read the audio.

    target_resolution:
      Set to (desired_height, desired_width) to have ffmpeg resize the frames
      before returning them. This is much faster than streaming in high-res
      and then resizing. If either dimension is None, the frames are resized
      by keeping the existing aspect ratio.

    resize_algorithm:
      The algorithm used for resizing. Default: "bicubic", other popular
      options include "bilinear" and "fast_bilinear". For more information, see
      https://ffmpeg.org/ffmpeg-scaler.html

    fps_source:
      The fps value to collect from the metadata. Set by default to 'tbr', but
      can be set to 'fps', which may be helpful if importing slow-motion videos
      that get messed up otherwise.


    Attributes
    -----------

    filename:
      Name of the original video file.

    fps:
      Frames per second in the original file.
    
    
    Read docs for Clip() and VideoClip() for other, more generic, attributes.
    
    Lifetime
    --------
    
    Note that this creates subprocesses and locks files. If you construct one of these instances, you must call
    close() afterwards, or the subresources will not be cleaned up until the process ends.
    
    If copies are made, and close() is called on one, it may cause methods on the other copies to fail.  

    """

    def __init__(self, filename, has_mask=False,
                 audio=True, audio_buffersize=200000,
                 target_resolution=None, resize_algorithm='bicubic',
                 audio_fps=44100, audio_nbytes=2, verbose=False,
                 fps_source='tbr'):

        VideoClip.__init__(self)

        # Make a reader
        pix_fmt = "rgba" if has_mask else "rgb24"
        self.reader = FFMPEG_VideoReader(filename, pix_fmt=pix_fmt,
                                         target_resolution=target_resolution,
                                         resize_algo=resize_algorithm,
                                         fps_source=fps_source)

        # Make some of the reader's attributes accessible from the clip
        self.duration = self.reader.duration
        self.end = self.reader.duration

        self.fps = self.reader.fps
        self.size = self.reader.size
        self.rotation = self.reader.rotation

        self.filename = self.reader.filename

        if has_mask:

            self.make_frame = lambda t: self.reader.get_frame(t)[:,:,:3]
            mask_mf = lambda t: self.reader.get_frame(t)[:,:,3]/255.0
            self.mask = (VideoClip(ismask=True, make_frame=mask_mf)
                         .set_duration(self.duration))
            self.mask.fps = self.fps

        else:

            self.make_frame = lambda t: self.reader.get_frame(t)

        # Make a reader for the audio, if any.
        if audio and self.reader.infos['audio_found']:

            self.audio = AudioFileClip(filename,
                                       buffersize=audio_buffersize,
                                       fps=audio_fps,
                                       nbytes=audio_nbytes)

    def imdisplay(self, imarray, screen=None):
        """Splashes the given image array on the given pygame screen """
        a = pg.surfarray.make_surface(imarray.swapaxes(0, 1))
        if screen is None:
            screen = pg.display.set_mode(imarray.shape[:2][::-1])
        screen.blit(a, (0, 0))
        pg.display.flip()

    def preview(self, clip, fps=15, audio=True, audio_fps=22050, audio_buffersize=3000,
                audio_nbytes=2, fullscreen=False):
        """
        Displays the clip in a window, at the given frames per second
        (of movie) rate. It will avoid that the clip be played faster
        than normal, but it cannot avoid the clip to be played slower
        than normal if the computations are complex. In this case, try
        reducing the ``fps``.

        Parameters
        ------------

        fps
          Number of frames per seconds in the displayed video.

        audio
          ``True`` (default) if you want the clip's audio be played during
          the preview.

        audio_fps
          The frames per second to use when generating the audio sound.

        fullscreen
          ``True`` if you want the preview to be displayed fullscreen.

        """
        if fullscreen:
            flags = pg.FULLSCREEN
        else:
            flags = 0

        # compute and splash the first image
        screen = pg.display.set_mode(clip.size, flags)

        img = clip.get_frame(0)
        self.imdisplay(img, screen)

        result = []

        t0 = time.time()
        for t in np.arange(1.0 / fps, clip.duration - .001, 1.0 / fps):

            img = clip.get_frame(t)

            for event in pg.event.get():
                if event.type == pg.QUIT or \
                        (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    return result

            t1 = time.time()
            time.sleep(max(0, t - (t1 - t0)))
            self.imdisplay(img, screen)

    def close(self):
        """ Close the internal reader. """
        if self.reader:
            self.reader.close()
            self.reader = None

        try:
            if self.audio:
                self.audio.close()
                self.audio = None
        except AttributeError:
            pass
