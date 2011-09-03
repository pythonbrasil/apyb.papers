# -*- coding:utf-8 -*

import json
from datetime import datetime

from Acquisition import aq_parent

from five import grok
from plone.directives import dexterity, form
from z3c.relationfield.schema import RelationChoice, RelationList

from Acquisition import aq_inner, aq_parent
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from z3c.formwidget.query.interfaces import IQuerySource

from zope import schema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import Interface, implements
from zope.schema.interfaces import IContextSourceBinder

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from collective.z3cform.datagridfield import DataGridFieldFactory, IDataGridField
from collective.z3cform.datagridfield import DictRow

from plone.formwidget.autocomplete.widget import AutocompleteMultiSelectionWidget

from Products.CMFPlone.utils import normalizeString

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from apyb.papers import MessageFactory as _
from zope.interface import  implementer
import z3c.form.interfaces
import z3c.form.widget

class SpeakerWidget(AutocompleteMultiSelectionWidget):
    ''' Override input template for AutocompleteMultiFieldWidget '''
    
    input_template = ViewPageTemplateFile('talk_templates/input.pt')
    
    def new_speaker_url(self):
        ''' Return an url to @@new-speaker '''
        context = aq_inner(self.context)
        
        while context.portal_type not in ['apyb.papers.program','Plone Site',]:
            context = aq_parent(context)
        if context.portal_type == 'apyb.papers.program':
            program_url = context.absolute_url()
            return '%s/@@new-speaker' % program_url

@implementer(z3c.form.interfaces.IFieldWidget)
def SpeakerFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field,
        SpeakerWidget(request))


class SpeakerSource(object):
    implements(IQuerySource)

    def __init__(self, context):
        self.context = aq_inner(context)
    
    @property
    def speakers(self):
        return self.find_speakers()
    
    @property
    def all_speakers(self):
        return self.find_speakers(filter=False)
    
    def find_speakers(self, filter=True):
        mt = getToolByName(self.context,'portal_membership')
        ct = getToolByName(self.context,'portal_catalog')
        member = mt.getAuthenticatedMember()
        rolesHere = member.getRolesInContext(self.context)
        dictSearch = {'portal_type':'apyb.papers.speaker','sort_on':'sortable_title'}
        if filter and not [r for r in rolesHere if r in ['Manager','Reviewer']]:
            # Only list profiles created by this user
            dictSearch['Creator'] = member.getUserName()
        return ct.searchResults(**dictSearch)
        
    @property
    def vocab(self):
        return SimpleVocabulary([SimpleTerm(b.UID,b.UID,b.Title) for b in self.speakers if hasattr(b,'UID')])
    
    @property
    def unfiltered_vocab(self):
        return SimpleVocabulary([SimpleTerm(b.UID,b.UID,b.Title) for b in self.all_speakers if hasattr(b,'UID')])
    
    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        try:
            term = self.vocab.getTerm(value)
        except LookupError:
            term = self.unfiltered_vocab.getTerm(value)
        return term

    def getTermByToken(self, value):
        try:
            term = self.vocab.getTermByToken(value)
        except LookupError:
            term = self.unfiltered_vocab.getTermByToken(value)
        return term
    
    def normalizeString(self,value):
        context = self.context
        return normalizeString(value,context).lower()
    
    def search(self, query_string):
        q = self.normalizeString(query_string)
        return [self.getTerm(b.UID) for b in self.speakers if q in self.normalizeString(b.Title)]


class SpeakerSourceBinder(object):
    implements(IContextSourceBinder)

    def __call__(self, context):
        return SpeakerSource(context)


class ITalkReference(Interface):
    ''' A talk reference'''
    
    ref_type = schema.Choice(
                    title=_(u'Reference type'),
                    description=_(u'Type of this reference'),
                    required=True,
                    vocabulary='apyb.papers.talk.referencetype',
    )
    
    url = schema.TextLine(
       title=_(u'URL'),
       description=_(u'Please provide a link to the reference'),
       required=True,
    )
    
    description = schema.TextLine(
       title=_(u'Description'),
       description=_(u'Please provide a brief description of this reference'),
       required=True,
    )
    


class ITalk(form.Schema):
    """
    A talk proposal
    """
    form.omitted('uid')
    uid = schema.Int(
        title=_(u"uid"),
        required=False,
        )
    #
    form.widget(speakers=SpeakerFieldWidget)
    speakers = schema.List(
        title=_(u'Speaker'),
        description=_(u'Please fill in the name of the speaker. If no speaker profile was created for this name, click on Add new speaker'),
        default=[],
        value_type=schema.Choice(title=_(u"Speaker"),
                                 source=SpeakerSourceBinder()),
        required=True,
        )
    #
    title = schema.TextLine(
        title=_(u'Talk Title'),
        description=_(u'Inform a talk title'),
        required=True,
    )
    #
    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    text = schema.Text(
        title=_(u"Talk details"),
        required=True,
        description=_(u"A description of this talk"),
    )
    #
    dexterity.read_permission(talk_type='zope2.View')
    dexterity.write_permission(talk_type='apyb.papers.AllocateTalk')
    talk_type = schema.Choice(
        title=_(u"Talk type"),
        required=True,
        description=_(u"Which type of talk best describes this one"),
        vocabulary='apyb.papers.talk.type',
    )
    #
    language = schema.Choice(
        title=_(u"Language"),
        required=True,
        description=_(u"Speaker's language"),
        vocabulary='apyb.papers.languages',
    )
    #
    track = schema.Choice(
        title=_(u"Track"),
        required=True,
        description=_(u"Which track this talk is"),
        vocabulary='apyb.papers.talk.track',
    )
    # 
    level = schema.Choice(
        title=_(u"Level"),
        required=True,
        description=_(u"Level of this talk"),
        vocabulary='apyb.papers.talk.level',
    )
    #
    form.widget(references='collective.z3cform.datagridfield.DataGridFieldFactory')
    references = schema.List(
        title=_(u"References"),
        required=False,
        description=_(u"References for this talk"),
        value_type=DictRow(title=_(u'Reference'), 
                                schema=ITalkReference),
    )
    #
    iul = schema.Bool(
        title=_(u"Do you allow your image to be used in post-conference videos?"),
        required=False,
        default=True,
    )
    #
    form.fieldset('allocation',
            label=_(u"Talk Allocation"),
            fields=['startDate','endDate','location']
    )
    
    dexterity.read_permission(location='zope2.View')
    dexterity.write_permission(location='apyb.papers.AllocateTalk')    
    location = schema.Choice(
        title=_(u"Location"),
        required=False,
        description=_(u"Room where this talk will be presented"),
        vocabulary='apyb.papers.talk.rooms',
    )
    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='apyb.papers.AllocateTalk')
#    form.widget(startDate='collective.z3cform.datetimewidget.DatetimeWidget')
    startDate = schema.Datetime(
        title=_(u"Start date"),
        required=False,
        description=_(u"Talk start date"),
    )
    #
    dexterity.read_permission(endDate='zope2.View')
    dexterity.write_permission(endDate='apyb.papers.AllocateTalk')
#    form.widget(endDate='collective.z3cform.datetimewidget.DatetimeWidget')
    endDate = schema.Datetime(
        title=_(u"End date"),
        required=False,
        description=_(u"Talk end date"),
    )
    #
    form.fieldset('material',
            label=_(u"Talk materials"),
            fields=['presentation','video','files']
    )
    
    dexterity.read_permission(presentation='zope2.View')
    dexterity.write_permission(presentation='apyb.papers.AllocateTalk')
    presentation = schema.TextLine(
        title=_(u"Presentation file"),
        required=False,
        description=_(u"Link to the presentation file"),
    )
    #
    dexterity.read_permission(video='zope2.View')
    dexterity.write_permission(video='apyb.papers.AllocateTalk')
    video = schema.TextLine(
        title=_(u"Presentation video"),
        required=False,
        description=_(u"Link to the presentation video"),
    )
    #
    dexterity.read_permission(files='zope2.View')
    dexterity.write_permission(files='apyb.papers.AllocateTalk')
    files = schema.TextLine(
        title=_(u"Presentation files"),
        required=False,
        description=_(u"Link to the presentation file downloads"),
    )
    #

class Talk(dexterity.Item):
    grok.implements(ITalk)
    
    def Title(self):
        return self.title
    
    def UID(self):
        return self.uid
    
    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)


class View(dexterity.DisplayForm):
    grok.context(ITalk)
    grok.require('zope2.View')
    
    def update(self):
        super(View,self).update()
        context = aq_inner(self.context)
        self.context = context
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self._wt = self.tools.workflow()
        self.member = self.portal.member()
        roles_context = self.member.getRolesInContext(context)
        if not self.show_border:
            self.request['disable_border'] = True    
    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()
    
    @property
    def show_references(self):
        ''' If this talk has references, show it '''
        context = self.context
        references = context.references
        return references
    
    def speaker_info(self):
        ''' return information about speakers to this talk '''
        speakers = self.context.speakers
        ct = self._ct
        results = ct.searchResults(portal_type='apyb.papers.speaker',UID=speakers)
        
        return results
    
class JSONView(View):
    grok.context(ITalk)
    grok.require('zope2.View')
    grok.name('json')
    
    template = None
    
    def speakers(self):
        ''' Return a list of speakers in here '''
        brains = super(JSONView,self).speaker_info()
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
    
    def render(self):
        request = self.request
        data = {'speakers':self.speakers()}
        data['url'] = self.context.absolute_url()
        data['title'] = self.context.title
        data['creation_date'] = self.context.CreationDate()
        data['track'] = aq_parent(self.context).Title()
        data['language'] = self.context.language
        data['talk_type'] = self.context.talk_type
        data['text'] = self.context.talk_type
        data['level'] = self.context.level
        data['votes'] = []
        data['state'] = self._wt.getInfoFor(self.context,'review_state')
                                        
        self.request.response.setHeader('Content-Type', 'application/json;charset=utf-8')
        return json.dumps(data,encoding='utf-8',ensure_ascii=False)