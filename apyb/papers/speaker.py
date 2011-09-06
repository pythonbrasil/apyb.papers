# -*- coding:utf-8 -*-
import json
from five import grok
from plone.directives import dexterity, form

from Acquisition import aq_inner
from zope.component import getMultiAdapter

from plone.namedfile.field import NamedImage

from zope import schema

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from apyb.papers import MessageFactory as _


class ISpeaker(form.Schema):
    """
    A speaker
    """
    
    form.omitted('uid')
    uid = schema.Int(
        title=_(u"uid"),
        required=False,
    )
    #
    fullname = schema.TextLine(
        title=_(u'Fullname'),
        description=_(u'Please inform your fullname'),
        required=True,
    )
    #
    description = schema.Text(
        title=_(u"Biografy"),
        required=True,
        description=_(u"A brief biografy"),
    )
    #
    organization = schema.TextLine(
        title=_(u"Organization"),
        required=True,
        description=_(u"Organization you represent"),
    )
    #
    email = schema.TextLine(
        title=_(u"Email"),
        required=True,
        description=_(u"Speaker's email"),
    )
    #
    home_page = schema.TextLine(
        title=_(u"Site"),
        required=True,
        description=_(u"Speaker's site"),
    )
    #
    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Speaker's language"),
        vocabulary='apyb.papers.languages',
    )
    #
    image = NamedImage(
        title=_(u"Portrait"),
        required=False,
        description=_(u"Upload an image to be used as speakers' portrait."),
    )
    


class Speaker(dexterity.Item):
    grok.implements(ISpeaker)
    
    def _get_title(self):
        return self.fullname
    def _set_title(self, value):
        pass
    title = property(_get_title, _set_title)
    
    def Title(self):
        return self.title
    
    def Description(self):
        return self.description
    
    def UID(self):
        return self.uid
    
    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)
    
    
class View(grok.View):
    grok.context(ISpeaker)
    grok.require('zope2.View')
    
    def update(self):
        super(View,self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.member = self.portal.member()
        roles_context = self.member.getRolesInContext(context)
        if not self.show_border:
            self.request['disable_border'] = True
    
    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()
    
    def speakers(self,speaker_uids):
        ''' Given a list os uids, we return a list of dicts with speakers data '''
        ct = self._ct
        brains = ct.searchResults(portal_type='apyb.papers.speaker',UID=speaker_uids)
        speakers = [{'name':b.Title,
                     'organization':b.organization,
                     'bio':b.Description,
                     'country':b.country,
                     'state':b.state,
                     'city':b.city,
                     'url':b.getURL(),
                     'json_url':'%s/json' % b.getURL(),
                     } 
                    for b in brains]
        return speakers
    
    def speaker_name(self,speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        ct = self._ct
        results = ct.searchResults(portal_type='apyb.papers.speaker',UID=speaker_uids)
        return ', '.join([b.Title for b in results])
     
    def my_talks(self):
        ''' Return a list of my talks '''
        results = self._ct.searchResults(portal_type='apyb.papers.talk', 
                                         speakers=[self.context.UID(),],
                                         sort_on='sortable_title')
        return results

class JSONView(View):
    grok.name('json')

    template = None

    def talks(self):
        ''' Return a list of talks in here '''
        brains = super(JSONView,self).my_talks()
        talks = []
        for brain in brains:
            talk = {}
            talk['creation_date'] = brain.CreationDate
            talk['title'] = brain.Title
            talk['description'] = brain.Description
            talk['track'] = self.context.title
            talk['speakers'] = self.speakers(brain.speakers)
            talk['language'] = brain.language
            talk['points'] = brain.points or 0.0
            talk['state'] = brain.review_state
            talk['url'] = '%s' % brain.getURL()
            talk['json_url'] = '%s/json' % brain.getURL()
            talks.append(talk)
        return talks

    def render(self):
        request = self.request
        talks = self.talks()
        data = {'name':self.context.title,
                'organization':self.context.organization,
                'bio':self.context.description,
                'country':self.context.country,
                'state':self.context.state,
                'city':self.context.city,
                'language':self.context.language,
                'url':self.context.absolute_url(),
               }
        data['talks'] = self.talks()

        self.request.response.setHeader('Content-Type', 'application/json;charset=utf-8')
        return json.dumps(data,encoding='utf-8',ensure_ascii=False)