# -*- coding:utf-8 -*-
import json

from five import grok

from Acquisition import aq_inner
from Acquisition import aq_parent

from zope.schema.interfaces import IVocabularyFactory
from zope.component import getMultiAdapter, queryUtility

from plone.directives import dexterity, form

from zope import schema

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from apyb.papers import MessageFactory as _


# Interface class; used to define content-type schema.

class IProgram(form.Schema):
    """
    Conference Program
    """


class Program(dexterity.Container):
    grok.implements(IProgram)
    
    # Add your class methods and properties here



class View(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    
    def update(self):
        super(View,self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.helper = getMultiAdapter((context, self.request), name=u'helper')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.is_anonymous = self.portal.anonymous()
        self.member = self.portal.member()
        self.stats = self.helper.program_stats()
        roles_context = self.member.getRolesInContext(context)
        if not self.show_border:
            self.request['disable_border'] = True
    
    @property
    def can_submit(self):
        ''' This user can submit a talk in here'''
        return self._mt.checkPermission('apyb.papers: Add Talk',self.context)
    
    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()
    
    @property
    def login_url(self):
        return '%s/login' % self.portal.portal_url()
    
    @property
    def register_url(self):
        return '%s/@@register' % self.portal.portal_url()
    
    def speaker_name(self,speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        helper = self.helper
        speakers_dict = helper.speakers_dict
        results = [speaker for uid,speaker in speakers_dict.items() if uid in speaker_uids]
        return ', '.join([b['name'] for b in results])
    
    def tracks(self):
        ''' Return a list of tracks in here '''
        helper = self.helper
        results = helper.tracks(sort_on='getObjPositionInParent')
        return results
    
    def speakers(self):
        ''' Return a list of speakers in here '''
        helper = self.helper
        results = helper.speakers(sort_on='sortable_title')
        return results
    
    def talks(self):
        ''' Return a list of talks in here '''
        helper = self.helper
        results = helper.talks(sort_on='sortable_title')
        return results
    
    def my_talks(self):
        ''' Return a list of my talks '''
        helper = self.helper
        results = helper.talks_username(username=self.member.getUserName(),sort_on='sortable_title',)
        return results
    
    def my_talks_accepted(self):
        ''' Return a list of my talks waiting for confirmation '''
        helper = self.helper
        results = helper.talks_username(username=self.member.getUserName(),review_state='accepted',sort_on='sortable_title',)
        return results
        
    def my_talks_confirmed(self):
        ''' Return a list of my talks waiting for confirmation '''
        helper = self.helper
        results = helper.talks_username(username=self.member.getUserName(),review_state='confirmed',sort_on='sortable_title',)
        return results
    
    def my_profiles(self):
        ''' Return a list of my speaker profiles '''
        helper = self.helper
        results = helper.speakers_username(username=self.member.getUserName(),sort_on='sortable_title')
        return results
    
    def last_talks(self):
        ''' Return a list of the last 5 talks in here '''
        helper = self.helper
        results = helper.talks(sort_on='created',
                               sort_order='reverse',
                               sort_limit=5,)
        return results[:5]


class TalksView(View):
    grok.name('talks')

    def track_info(self,track_uid):
        helper = self.helper
        return helper.track_info(track_uid)
    
    def talks_confirmed(self):
        ''' Return a list of confirmed talks '''
        helper = self.helper
        results = helper.talks(review_state='confirmed',sort_on='sortable_title',)
        return results 

class JSONView(View):
    grok.name('json')
    
    template = None
    
    def update(self):
        super(JSONView,self).update()
        self._tracks = dict([(b.UID,b) for b in super(JSONView,self).tracks()])
        self._speakers = dict([(b.UID,b) for b in super(JSONView,self).tracks()])
        self._talks = dict([(b.UID,b) for b in super(JSONView,self).tracks()])
    
    def speakers_info(self,speakers):
        ''' Return a list of speakers in here '''
        brains = self._ct.searchResults(portal_type='apyb.papers.speaker',
                                         path=self._path,
                                         UID=speakers, 
                                         sort_on='sortable_title')
        speakers = []
        for brain in brains:
            speaker = {'name':brain.Title,
                       'organization':brain.organization,
                       'bio':brain.Description,
                       'country':brain.country,
                       'state':brain.state,
                       'city':brain.city,
                       'language':brain.language,
                       'url':brain.getURL(),
                       'json_url':'%s/json' % brain.getURL(),
                       }
            speakers.append(speaker)
        return speakers
    
    def talks(self,track):
        ''' Return a list of talks in here '''
        brains = self._ct.searchResults(portal_type='apyb.papers.talk',
                                         track=track,
                                         path=self._path,
                                         sort_on='sortable_title')
        talks = []
        for brain in brains:
            talk = {}
            talk['creation_date'] = brain.CreationDate
            talk['title'] = brain.Title
            talk['description'] = brain.Description
            talk['track'] = self.context.title
            talk['speakers'] = self.speakers_info(brain.speakers)
            talk['language'] = brain.language
            talk['points'] = brain.points or 0.0
            talk['state'] = brain.review_state
            talk['url'] = '%s' % brain.getURL()
            talk['json_url'] = '%s/json' % brain.getURL()
            talks.append(talk)
        return talks
    
    def tracks(self):
        ''' Return a list of tracks in here '''
        brains = super(JSONView,self).tracks()
        tracks = []
        for brain in brains:
            track = {}
            track['title'] = brain.Title
            track['description'] = brain.Description
            track['talks'] = self.talks(brain.UID)
            track['url'] = '%s' % brain.getURL()
            track['json_url'] = '%s/json' % brain.getURL()
            tracks.append(track)
        return tracks
    
    def render(self):
        request = self.request
        data = {'tracks':self.tracks()}
        data['url'] = self.context.absolute_url()
        data['title'] = self.context.title
        
        self.request.response.setHeader('Content-Type', 'application/json;charset=utf-8')
        return json.dumps(data,encoding='utf-8',ensure_ascii=False)


class Speakers(grok.View):
    grok.context(IProgram)
    grok.require('cmf.ReviewPortalContent')
    grok.name('speakers')
    
    def update(self):
        super(Speakers,self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.helper = getMultiAdapter((context, self.request), name=u'helper')
        self._ct = self.tools.catalog()
        self.member = self.portal.member()
        roles_context = self.member.getRolesInContext(context)
        self.voc = queryUtility(IVocabularyFactory, 'apyb.papers.languages')(self.context)
        # Remove Portlets
        self.request['disable_plone.leftcolumn']=1
        self.request['disable_plone.rightcolumn']=1
        
        if not self.show_border:
            self.request['disable_border'] = True
    
    def talks_speakers(self,**kw):
        ''' Return a dict of talks per speaker '''
        helper = self.helper
        return helper.talks_speaker()
    
    def keynote_speakers(self):
        ''' List uids of keynote speakers
        '''
        keynote_talks = self._ct.searchResults(portal_type='apyb.papers.talk',
                                               path='%s/keynotes' % self._path,        
                                               sort_on='sortable_title')
        speakers = []
        for talk in keynote_talks:
            for speaker in talk.speakers:
                if not speaker:
                    speakers.append(speaker)
        return speakers
    
    def speakers_info(self,keynotes=False):
        ''' Return a tuple of names and emails of speakers with 
            talks in here.
        '''
        speakers = self.speakers()
        talks_speakers = self.talks_speakers()
        speakers_info = []
        exclude = []
        if keynotes:
            exclude = self.keynote_speakers()
        for speaker in speakers:
            uid = speaker.UID
            talks = talks_speakers.get(speaker.UID,[])
            if not talks or uid in exclude:
                continue
            speakers_info.append((speaker.email,speaker.Title,self.speaker_registered(speaker.email)))
        return speakers_info
    
    def speaker_registered(self,email):
        ''' Is this speaker registered to the conference '''
        status = u'Não'
        results = self._ct.searchResults(portal_type='apyb.registration.attendee',
                                         email=email,
                                         sort_on='sortable_title')
        if results:
            status = results[0].review_state
        return status
    
    def speakers(self):
        ''' Return a list of speakers in here '''
        results = self._ct.searchResults(portal_type='apyb.papers.speaker',
                                         path=self._path,        
                                         sort_on='sortable_title')
        return results
    
    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()
    

    
class ConfirmView(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    grok.name('confirm-talks')
    
    template = None
    
    def update(self):
        super(ConfirmView,self).update()
        context = aq_inner(self.context)
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.helper = getMultiAdapter((context, self.request), name=u'helper')
        self._ct = self.tools.catalog()
        self._wt = self.tools.workflow()
        self.member = self.portal.member()
        
    
    def my_talks_accepted(self):
        ''' Return a list of my talks waiting for confirmation '''
        helper = self.helper
        results = helper.talks_username(username=self.member.getUserName(),review_state='accepted',sort_on='sortable_title',)
        return results
    
    def render(self):
        talks = self.my_talks_accepted()
        talks = dict([(str(b.UID),b) for b in talks])
        for talk_uid,brain in talks.items():
            action = self.request.form.get(talk_uid,'')
            if not action in ['confirm','cancel']:
                continue
            o = brain.getObject()
            self._wt.doActionFor(o,action)
        return self.request.response.redirect(self.context.absolute_url())
        
    

class Ranking(View):
    grok.context(IProgram)
    grok.require('zope2.View')
    grok.name('ranking')
    
    def tracks_uids(self):
        ''' List of track uids excluding keynotes and pssa '''
        return [b.UID for b in self.tracks() if not b.getId in ['plone-symposium-south-america','keynotes']]
    
    def ordered_talks(self):
        helper = self.helper
        kw = {}
        kw['track'] = tuple(self.tracks_uids())
        kw['sort_on'] = 'points'
        kw['sort_order'] = 'reverse'
        results = helper.talks(**kw)
        return results
    
