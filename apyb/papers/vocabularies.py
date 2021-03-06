# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from sc.base.grokutils import registerSimpleVocabulary
from apyb.papers import MessageFactory as _


registerSimpleVocabulary(
    "ReferenceType", u"apyb.papers.talk", 
     [
      ('article',_(u'Article / Post')),
      ('presentation',_(u'Presentation')),
      ('video',_(u'Video')),
     ],
    globals()
)

registerSimpleVocabulary(
    "Type", u"apyb.papers.talk", 
    [
     ('talk',_(u'Talk')),
     ('panel',_(u'Panel')),
    ],
    globals()
)

def trackVocabulary(context):
    """Vocabulary factory for talk track options
    """
    ct = getToolByName(context,'portal_catalog')
    tracks = ct.searchResults(portal_type='apyb.papers.track', sort_on='getObjPositionInParent')
    items = [SimpleTerm(b.UID,b.UID,b.Title) for b in tracks]
    return SimpleVocabulary(items)

registerSimpleVocabulary(
    "Track", u"apyb.papers.talk", 
    trackVocabulary,
    globals()
)

registerSimpleVocabulary(
    "Level", u"apyb.papers.talk", 
    [('basic',_(u'Basic')),
     ('intermediate',_(u'Intermediate')),
     ('advanced',_(u'Advanced')),
    ],
    globals()
)

registerSimpleVocabulary(
    "Rooms", u"apyb.papers.talk",
    [
     ('dorneles-tremea',_(u'Auditório Dorneles Treméa')),
     ('cleese',_(u'Sala John Cleese')),
     ('idle',_(u'Sala Eric Idle')),
     ('gillian',_(u'Sala Terry Gilliam')),
     ('amcham',_(u'AMCHAM Business Center')),
     ('globalcode',_(u'GlobalCode')),
     ('outro',_(u'---')),
    ],
    globals()
)
  

def speakersVocabulary(context):
    """Vocabulary factory for speakers
    """
    ct = getToolByName(context,'portal_catalog')
    dictSearch = {'portal_type':'apyb.papers.speaker','sort_on':'sortable_title'}
    speakers = ct.searchResults(**dictSearch)
    speakers = [SimpleTerm(b.UID,b.UID,b.Title) for b in speakers]
    return SimpleVocabulary(speakers)

registerSimpleVocabulary(
    "Speakers", u"apyb.papers",
    speakersVocabulary,
    globals()
)

registerSimpleVocabulary(
    "Languages", u"apyb.papers",
    [
      ('pt_BR',_(u'Portuguese')),
      ('en',_(u'English')),
      ('es',_(u'Spanish')),
    ],
    globals()
)
 
def trainingsVocabulary(context):
    """Vocabulary factory for speakers
    """
    ct = getToolByName(context,'portal_catalog')
    dictSearch = {'portal_type':'apyb.papers.training',
                  'sort_on':'sortable_title',
                  'review_state':'confirmed'}
    trainings = ct.searchResults(**dictSearch)
    trainings = [SimpleTerm(b.UID,b.UID,b.Title) for b in trainings]
    return SimpleVocabulary(trainings)

registerSimpleVocabulary(
    "Trainings", u"apyb.papers",
    trainingsVocabulary,
    globals()
)