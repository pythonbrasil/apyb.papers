# -*- coding: utf-8 -*-
from five import grok
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from apyb.papers import MessageFactory as _

class RefTypeVocabulary(object):
    """Vocabulary factory for referene type options
    """
    grok.implements(IVocabularyFactory)
    
    def __call__(self, context):
        types = [('article',_(u'Article / Post')),
                 ('presentation',_(u'Presentation')),
                 ('video',_(u'Video')),
                 ]
        items = [SimpleTerm(k,k,v) for k,v in types]
        return SimpleVocabulary(items)

grok.global_utility(RefTypeVocabulary, name=u"apyb.papers.talk.referencetype")

class TypeVocabulary(object):
    """Vocabulary factory for talk type options
    """
    grok.implements(IVocabularyFactory)
    
    def __call__(self, context):
        types = [('talk',_(u'Talk')),
                 ('panel',_(u'Panel')),
                 ]
        items = [SimpleTerm(k,k,v) for k,v in types]
        return SimpleVocabulary(items)

grok.global_utility(TypeVocabulary, name=u"apyb.papers.talk.type")

class TrackVocabulary(object):
    """Vocabulary factory for talk track options
    """
    grok.implements(IVocabularyFactory)
    
    def __call__(self, context):
        #TODO
        tracks = [('plone',_(u'Plone')),
                  ('django',_(u'Django')),
                 ]
        items = [SimpleTerm(k,k,v) for k,v in tracks]
        return SimpleVocabulary(items)

grok.global_utility(TrackVocabulary, name=u"apyb.papers.talk.track")


class LevelVocabulary(object):
    """Vocabulary factory for talk level options
    """
    grok.implements(IVocabularyFactory)
    
    def __call__(self, context):
        levels = [('basic',_(u'Basic')),
                  ('intermediate',_(u'Intermediate')),
                  ('advanced',_(u'Advanced')),
                 ]
        items = [SimpleTerm(k,k,v) for k,v in levels]
        return SimpleVocabulary(items)

grok.global_utility(LevelVocabulary, name=u"apyb.papers.talk.level")

class RoomVocabulary(object):
    """Vocabulary factory for room options
    """
    grok.implements(IVocabularyFactory)
    
    def __call__(self, context):
        rooms = [
                 ('room1',_(u'Room 1')),
                 ('room2',_(u'Room 2')),
                 ]
        items = [SimpleTerm(k,k,v) for k,v in rooms]
        return SimpleVocabulary(items)

grok.global_utility(RoomVocabulary, name=u"apyb.papers.talk.rooms")

class SpeakersVocabulary(object):
    """Vocabulary factory for speakers
    """
    grok.implements(IVocabularyFactory)
    
    def __call__(self, context):
        ct = getToolByName(context,'portal_catalog')
        speakers = ct.searchResults(portal_type='apyb.papers.speaker')
        speakers = [SimpleTerm(b.uid,b.uid,b.Title) for b in speakers]
        return SimpleVocabulary(speakers)

grok.global_utility(SpeakersVocabulary, name=u"apyb.papers.speakers")

