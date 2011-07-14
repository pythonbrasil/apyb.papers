# -*- coding:utf-8 -*-
from five import grok
from zope.interface import Interface, implements
from zope import schema
from zope import component
from zope.component import getMultiAdapter

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
from apyb.papers.speaker import ISpeaker
from apyb.papers.program import IProgram

from apyb.papers import MessageFactory as _

class ISpeakerForm(ISpeaker,IAddress):
    form.fieldset('speaker',
            label=_(u"About the speaker"),
            fields=['fullname','description','organization','email','home_page','country','state','city', 'image']
        )
    form.omitted('address')
    form.omitted('postcode')


class SpeakerForm(form.SchemaAddForm):
    ''' Speaker profile '''
    grok.context(IProgram)
    grok.require('apyb.papers.AddSpeaker')
    grok.name('new-speaker')
    
    label = _(u"Speaker Profile")
    
    schema = ISpeakerForm
    
    enable_form_tabbing = False
    
    def create(self, data):
        ''' Create objects '''
        speaker = createContent('apyb.papers.speaker',checkConstraints=True, **data)
        return speaker
    
    def add(self, object):
        speaker = object
        context = self.context
        speakerObj = addContentToContainer(context,speaker)
        self.immediate_view = "%s/%s" % (context.absolute_url(), speakerObj.id)

class ITalkForm(ITalk):
    ''' An interface representing a talk submission form '''
    
    form.fieldset('talk',
            label=_(u"About the talk"),
            fields=['title','text','talk_type','track','level',]
        )
    form.omitted('location')
    form.omitted('startDate')
    form.omitted('endDate')
    form.omitted('presentation')
    form.omitted('video')
    form.omitted('files')
    
    form.fieldset('metatalk',
        label=_(u"References for this talk"),
        fields=['references',]
    )
    
    form.fieldset('legal',
        label=_(u"Legal information"),
        fields=['iul',]
    )
    

class TalkForm(form.SchemaAddForm):
    ''' Talk submission form '''
    grok.context(IProgram)
    grok.require('apyb.papers.AddTalk')
    grok.name('new-talk')
    
    template = ViewPageTemplateFile('templates/new_talk.pt')
    
    label = _(u"Talk submission")
    
    schema = ITalkForm
    
    enable_form_tabbing = False
    
    def create(self, data):
        ''' Create objects '''
        talkfields = ['title','text','talk_type','track','level','references','iul',]
        talkinfo = dict([(k,data.get(k)) for k in talkfields])
        talk = createContent('apyb.papers.talk',checkConstraints=True, **talkinfo)
        
        return talk
    
    def add(self, object):
        talk = object
        context = self.context
        talkObj = addContentToContainer(context,talk)
        self.immediate_view = "%s/%s" % (context.absolute_url(), talkObj.id)
    

@form.default_value(field=ISpeakerForm['country'])
def default_country(data):
    return u'br'

@form.default_value(field=ISpeakerForm['email'])
def default_email(data):
    state = getMultiAdapter((data.context, data.request), name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('email')

@form.default_value(field=ISpeakerForm['fullname'])
def default_fullname(data):
    state = getMultiAdapter((data.context, data.request), name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('fullname')

@form.default_value(field=ISpeakerForm['home_page'])
def default_home_page(data):
    state = getMultiAdapter((data.context, data.request), name=u'plone_portal_state')
    member = state.member()
    return member.getProperty('home_page')
