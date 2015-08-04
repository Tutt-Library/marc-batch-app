"""
 :mod:`asp_jml` Alexander Street Press Jazz Library Job
"""
__author__ = "Jeremy Nelson"
from asp_base import AlexanderStreetPressMusicJob
NAME = "Alexander Street Press - Jazz Music Library"

class AlexanderStreetPressJazzMusicLibrary(AlexanderStreetPressMusicJob):

    def __init__(self,marc_file,**kwargs):
        """
        Creates instance of `AlexanderStreetPressJazzMusicLibrary`
        """
        
        kwargs['asp_code'] = 'jazz'
        kwargs['proxy'] = '0-jazz.alexanderstreet.com.tiger.coloradocollege.edu'
        super(AlexanderStreetPressJazzMusicLibrary,self).__init__(marc_file,
                                                                  **kwargs)





