"""
 :mod:`eai_evans` Early American Imprints Evans Job
"""
__author__ = "Jeremy Nelson"
from eai import EarlyAmericanImprintsJob
NAME = "Early American Imprints First Series (Evans)"

class EarlyAmericanImprintsEvansJob(EarlyAmericanImprintsJob):

    def __init__(self,marc_file,**kwargs):
        """
        Creates instance of `EarlyAmericanImprintsEvansJob`
        """
        kwargs['field500_stmt'] = 'Evans digital edition'
        kwargs['field730_series'] = 'First series'
        super(EarlyAmericanImprintsEvansJob,self).__init__(marc_file,**kwargs)



