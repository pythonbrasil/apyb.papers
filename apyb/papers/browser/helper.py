# -*- coding:utf-8 -*-
from five import grok

from Acquisition import aq_inner

from zope.schema.interfaces import IVocabularyFactory
from zope.component import getMultiAdapter, queryUtility

from plone.memoize.view import memoize

from apyb.papers.program import IProgram

from apyb.papers import MessageFactory as _

class View(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    grok.name('helper')
    
    def __init__(self, context, request):
        super(View,self).__init__(context,request)
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self.voc = {'languages':queryUtility(IVocabularyFactory, 'apyb.papers.languages')(context),
                   }
    
    def render(self):
        return ''
    
    def tracks(self,**kw):
        kw['portal_type'] = 'apyb.papers.track'
        kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains
    
    def talks(self,**kw):
        kw['portal_type'] = 'apyb.papers.talk'
        if not 'path' in kw:
            kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains
    
    def speakers(self,**kw):
        kw['portal_type'] = 'apyb.papers.speaker'
        kw['path'] = self._path
        brains = self._ct.searchResults(**kw)
        return brains
    
    @property
    def tracks_dict(self):
        brains = self.tracks()
        tracks = dict([(b.UID,{'title':b.Title,
                               'description':b.Description,
                               'review_state':b.review_state,
                               'url':b.getURL(),
                               'json_url':'%s/json' % b.getURL(),}) 
                    for b in brains])
        return tracks
    
    @property
    def talks_dict(self):
        brains = self.talks()
        talks = dict([(b.UID,{'title':b.Title,
                               'description':b.Description,
                               'track':b.track,
                               'speakers':b.speakers,
                               'language':b.language,
                               'level':b.level,
                               'review_state':b.review_state,
                               'url':b.getURL(),
                               'json_url':'%s/json' % b.getURL(),}) 
                    for b in brains])
        return talks
    
    @property
    def speakers_dict(self):
        brains = self.speakers()
        speakers = dict([(b.UID,{'name':b.Title,
                     'organization':b.organization,
                     'bio':b.Description,
                     'review_state':b.review_state,
                     'language':b.language,
                     'country':b.country,
                     'state':b.state,
                     'city':b.city,
                     'url':b.getURL(),
                     'json_url':'%s/json' % b.getURL(),
                     })
                    for b in brains])
        return speakers
    
    def track_info(self,uid):
        ''' Return track info for a given uid '''
        return self.tracks_dict.get(uid,{})
    
    def talk_info(self,uid):
        ''' Return talk info for a given uid '''
        return self.talks_dict.get(uid,{})
    
    def speaker_info(self,uid):
        ''' Return speaker info for a given uid '''
        return self.speakers_dict.get(uid,{})
    
    def speakers_username(self,username,**kw):
        # HACK: username is an email
        speakers_profiles = self.speakers(email=username)
        if not speakers_profiles:
            # Let's see if this user created a profile under a different email
            speakers_profiles = self.speakers(Creator=username)
        return speakers_profiles
    
    def talks_username(self,username,**kw):
        # HACK: username is an email
        speakers_profiles = [b.UID for b in self.speakers_username(username)]
        kw['speakers'] = speakers_profiles
        return self.talks(**kw)
    
    