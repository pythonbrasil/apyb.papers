# -*- coding:utf-8 -*-
from five import grok
from zope.interface import Interface, implements
from zope import schema
from zope import component
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from zope.app.intid.interfaces import IIntIds
from z3c.form import button, field, group
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE, IDataConverter, NO_VALUE
from z3c.form.form import applyChanges
from z3c.form.interfaces import IWidgets
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import createContent
from plone.directives import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.behavior.contactinfo.behavior.address import IAddress

from apyb.papers.talk import ITalk
from apyb.papers.talk import ITalkReference
from apyb.papers.track import ITrack
from apyb.papers.speaker import ISpeaker
from apyb.papers.program import IProgram

from apyb.papers import MessageFactory as _

class ITalkForm(ITalk):
    ''' An interface representing a talk submission form '''
    
    form.fieldset('speaker',
            label=_(u"About the speaker"),
            fields=['speakers',]
        )
    
    form.fieldset('talk',
            label=_(u"About the talk"),
            fields=['title','text','talk_type','track','language','level',]
    )
    form.omitted('points')
    form.omitted('votes')
    form.omitted('talk_type')
    form.omitted('location')
    form.omitted('startDate')
    form.omitted('endDate')
    form.omitted('presentation')
    form.omitted('video')
    form.omitted('files')
    
    form.omitted('references')
    form.fieldset('metatalk',
        label=_(u"References for this talk"),
        fields=['references',]
    )
    
    form.fieldset('legal',
        label=_(u"Legal information"),
        fields=['iul',]
    )

class ITrackTalkForm(ITalkForm):
    ''' An interface representing a talk submission form inside a track'''
    
    form.omitted('track')


class TalkForm(form.SchemaAddForm):
    ''' Talk submission form '''
    grok.context(IProgram)
    grok.require('apyb.papers.AddTalk')
    grok.name('new-talk')
    
    template = ViewPageTemplateFile('templates/new_talk.pt')
    
    label = _(u"Talk submission")
    description = _(u"")
    
    schema = ITalkForm
    
    inside_track = False
    enable_form_tabbing = False
    
    def track_object(self,talk):
        ''' Return Track which will host this talk '''
        if self.inside_track:
            track = self.context
        else:
            ct = getToolByName(self.context,'portal_catalog')
            results = ct.searchResults(portal_type='apyb.papers.track',UID=UID)
            if not results:
                # oops
                # something wrong happened, but let's be safe
                track = self.context
            else:
                track = results[0].getObject()
        
        return track
    
    def create(self, data):
        ''' Create objects '''
        talkfields = ['speakers','title','text','talk_type','track','language','level','references','iul',]
        talkinfo = dict([(k,data.get(k,'')) for k in talkfields])
        if self.inside_track:
            talkinfo['track'] = self.context.UID()
        talk = createContent('apyb.papers.talk',checkConstraints=True, **talkinfo)
        return talk
    
    def add(self, object):
        talk = object
        # We look for the right track to add the talk
        context = self.track_object(talk)
        talkObj = addContentToContainer(context,talk)
        self.immediate_view = "%s/%s" % (context.absolute_url(), talkObj.id)
    

class TrackTalkForm(TalkForm):
    ''' Talk submission form '''
    grok.context(ITrack)
    
    schema = ITrackTalkForm
    
    inside_track = True


@form.default_value(field=ITalkForm['speakers'])
def default_speakers(data):
    tools = getMultiAdapter((data.context, data.request), name=u'plone_tools')
    state = getMultiAdapter((data.context, data.request), name=u'plone_portal_state')
    ct = tools.catalog()
    member = state.member()
    email = member.getProperty('email')
    results = ct.searchResults(portal_type='apyb.papers.speaker',email=email)
    if results:
        # We consider the first result as the most important one
        brain = results[0]
        UID = brain.UID
        return [UID,]
