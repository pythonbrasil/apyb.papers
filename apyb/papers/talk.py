# -*- coding:utf-8 -*-
from five import grok
from plone.directives import dexterity, form
from z3c.relationfield.schema import RelationChoice, RelationList

from Acquisition import aq_inner, aq_parent

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
        self.context = context
        catalog = getToolByName(context, 'portal_catalog')
        self.speakers = catalog.searchResults(portal_type='apyb.papers.speaker')
        self.vocab = SimpleVocabulary([SimpleTerm(b.UID,b.UID,b.Title) for b in self.speakers if hasattr(b,'UID')])

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        return self.vocab.getTerm(value)

    def getTermByToken(self, value):
        return self.vocab.getTermByToken(value)
    
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
    talk_type = schema.Choice(
        title=_(u"Talk type"),
        required=True,
        description=_(u"Which type of talk best describes this one"),
        vocabulary='apyb.papers.talk.type',
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
    )
    #
    form.fieldset('allocation',
            label=_(u"Talk Allocation"),
            fields=['startDate','endDate','location']
    )
    
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
    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='apyb.papers.AllocateTalk')
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
    
    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='cmf.ModifyPortalContent')
    presentation = schema.TextLine(
        title=_(u"Presentation file"),
        required=False,
        description=_(u"Link to the presentation file"),
    )
    #
    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='cmf.ModifyPortalContent')
    video = schema.TextLine(
        title=_(u"Presentation video"),
        required=False,
        description=_(u"Link to the presentation video"),
    )
    #
    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='cmf.ModifyPortalContent')
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


class View(grok.View):
    grok.context(ITalk)
    grok.require('zope2.View')


