"""
 op.py - Oxford Press Base Class and Module
"""
__author__ = "Jeremy Nelson"

import urllib.request
import urllib.parse

from marc_helpers import MARCModifier
from pymarc import Field

NAME = "Oxford Handbooks Online"

HANDBOOK_PROXY_FILTER = 'http://0-www.oxfordhandbooks.com.tiger.coloradocollege.edu'

COLLECTIONS = [
    {"name": "Oxford Handbooks Online Archaeology",
     "handbook_label": "in archaeology"},
    {"name": "Oxford Handbooks Online Business and Management",
     "handbook_label": "in business and management"},
    {"name": "Oxford Handbooks Online Philosophy",
     "handbook_label": "in classics and ancient history"},
    {"name":  "Oxford Handbooks Online Economics and Finance",
     "handbook_label": "in economics and finance"},
    {"name": "Oxford Handbooks Online History",
     "handbook_label": "in history"},
    {"name": "Oxford Handbooks Online Literature",
     "handbook_label": "of literature"},
    {"name": "Oxford Handbooks Online Music",
     "handbook_label": "in music"},
    {"name": "Oxford Handbooks Online Philosophy",
     "handbook_label": "in philosophy"},
    {"name": "Oxford Handbooks Online Political Science",
     "handbook_label": 'of political science'},
    {"name":  "Oxford Handbooks Online Psychology",
     "handbook_label": "of psychology"},
    {"name":  "Oxford Handbooks Online Psychology",
      "handbook_label":  "of psychology"},
    {"name": "Oxford Handbooks Online Religion",
     "handbook_label": 'in religion'}
]

class OxfordHandbooksJob(MARCModifier):
    """
    Class reads Oxford Handbooks Online MARC records, validates,
    and adds/modifies fields of each MARC record for importing into
    TIGER iii ILS.
    """

    def __init__(self,**kwargs):
        """
        Initializes `OxfordHandbooksJob`

        :keyword marc_file: Required input MARC file object from Oxford Handbooks
        :keyword proxy_filter: Optional, proxy prefix for 856 field default is HANDBOOK_PROXY_FILTER
                               constant.
        :keyword public_note: Optional, default is 'View Online'
        :keyword note_prefix: Optional 538 note prefix, default is 'Available via Internet'
        :keyword type_of: Optional, used when specific collections are loaded, used for XXX
                          field.
        """
        marc_file = kwargs.get('marc_file')
        collection = kwargs.get('collection')
        self.handbook_label = None
        for row in collection:
            if row.get('name') == collection:
                self.handbook_label = row.get('handbook_label')        
        if not self.handbook_label:
            raise ValueError("Collection required to set handbook label") 
        to_unicode = kwargs.get('to_unicode', False)
        MARCModifier.__init__(self, marc_file, to_unicode)
        if kwargs.has_key('proxy_filter'):
            self.proxy_filter = kwargs.get('proxy_filter')
        else:
            self.proxy_filter = HANDBOOK_PROXY_FILTER
        if kwargs.has_key('public_note'):
            self.public_note = kwargs.get('public_note')
        else:
            self.public_note = 'View online'
        if kwargs.has_key('note_prefix'):
            self.note_prefix = kwargs.get('note_prefix')
        else:
            self.note_prefix='Available via Internet'


    def processRecord(self,marc_record):
        """
        Method process record and is called by `MARCImportBot` load method.

        :param marc_record: Required input MARC file from Oxford Reference,
                            should have been set when instance was initialized.
        """
        #marc_record.leader = self.processLeader(marc_record.leader)
        marc_record = self.remove050(marc_record)
        marc_record = self.remove082(marc_record)
        marc_record = self.validate006(marc_record)
        marc_record = self.validate007(marc_record)
        marc_record = self.validate300(marc_record)
        marc_record = self.remove490(marc_record)
        marc_record = self.validate506(marc_record)
        marc_record = self.remove530(marc_record)
        marc_record = self.validate730(marc_record)
        marc_record = self.remove830(marc_record)
        marc_record = self.processOxfordHandbookURLS(marc_record)
        return marc_record

    def processOxfordHandbookURLS(self,marc_record):
        """
        Method overrides parent processURLS for Oxford Handbook URL  specific
        modification of the 538 and 856 fields

        :param marc_record: MARC record, required
        """
        all856fields = marc_record.get_fields('856')
        field856 = all856fields[0]
        # Remove existing 856 fields
        for field in all856fields:
            marc_record.remove_field(field)
        doi_url = field856.get_subfields('u')[0]
        try:
            # Retrieve DOI link (redirects to Oxford Handbook URL)
            doi_request = urllib.request.urlopen(doi_url)
            ohb_url = doi_request.geturl()
            ohb_path = urllib.parse.urlparse.urlsplit(ohb_url).path
        except:
            ohb_url = ''
            ohb_path = urllib.parse.urlparse.urlsplit(doi_url).path

        # Create new 538 field
        new538 = Field(tag='538',
                       indicators=[" "," "],
                       subfields=['a','{}, {}'.format(self.note_prefix,
                                                      ohb_url)])
        marc_record.add_field(new538)
        # Create new 856 field
        new856 = Field(tag='856',
                       indicators=['4','0'],
                       subfields=['u','{}{}'.format(self.proxy_filter,
                                                ohb_path),
                                  'z',self.public_note])
        marc_record.add_field(new856)
        return marc_record

    def remove082(self,marc_record):
        """
        Removes the 082 field.

        :param marc_record: MARC record, required
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='082')


    def remove490(self,marc_record):
        """
        Method removes the 490 field.

        :param marc_record: MARC record, required
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='490')

    def remove830(self,marc_record):
        """
        Method removes the 830 field.

        :param marc_record: MARC record, required
        """
        return self.__remove_field__(marc_record=marc_record,
                                     tag='830')

    def validate006(self, marc_record):
        """Method validates 006 field, sets 'o' value for online in position 6

        :param marc_record: MARC record, required
        """
        field006 = marc_record.get_fields('006')[0]
        org_data = field006.data
        marc_record.remove_field(field006)
        if org_data[6] != 'o':
            org_data = org_data[:6] + r'o' + org_data[7:]
        field006.data = org_data
        marc_record.add_field(field006)
        return marc_record

    def validate007(self,marc_record):
        """
        Method validates 007 field, sets position 13 to u

        :param marc_record: MARC record, required
        """
        field007 = marc_record.get_fields('007')[0]
        org_data = field007.data
        marc_record.remove_field(field007)
        if org_data[13] != 'u':
            org_data = org_data[:13] + r'u'
        field007.data = org_data
        marc_record.add_field(field007)
        return marc_record

    def validate506(self, marc_record):
        """
        Method adds a 506 fixed field

        :param marc_record: MARC record, required
        """
        field506 = Field(
             tag='506',
             indicators=[' ', ' '],
             subfields=['a', 'Access restricted to subscribing institutions.'])
        marc_record.add_field(field506)
        return marc_record

    def validate730(self,marc_record):
        """
        Method creates two 730 fields with specific collection set for subfield
        a.

        :param marc_record: MARC record, required
        """
        marc_record = self.__remove_field__(marc_record=marc_record,
                                            tag='730')
        first730 = Field(tag='730',
                         indicators=['0',' '],
                         subfields=['a','Oxford handbooks online.'])
        marc_record.add_field(first730)
        if self.handbook_label:
            new730 = Field(tag='730',
                           indicators=['0',' '],
                           subfields=['a', 'Oxford handbooks {}'.format(
                                             self.handbook_label.lower())])
            marc_record.add_field(new730)
        return marc_record
