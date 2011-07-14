# -*- coding:utf-8 -*-
from five import grok
from plone.directives import dexterity, form

from zope import schema

from zope.interface import Interface, implements

from collective.z3cform.datagridfield import DataGridFieldFactory, IDataGridField
from collective.z3cform.datagridfield import DictRow

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from apyb.papers import MessageFactory as _

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
    title = schema.TextLine(
        title=_(u'Talk Title'),
        description=_(u'Inform a talk title'),
        required=True,
    )
    #
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
        title=_(u"Do you allow your image to be used in post-conference videos?""),
        required=False,
    )
    #
    startDate = schema.Date(
        title=_(u"Start date"),
        required=False,
        description=_(u"Talk start date"),
    )
    #
    endDate = schema.Date(
        title=_(u"End date"),
        required=False,
        description=_(u"Talk end date"),
    )
    #
    presentation = schema.TextLine(
        title=_(u"Presentation file"),
        required=False,
        description=_(u"Link to the presentation file"),
    )
    #
    video = schema.TextLine(
        title=_(u"Presentation video"),
        required=False,
        description=_(u"Link to the presentation video"),
    )
    #
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
    
    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)


class SampleView(grok.View):
    grok.context(ITalk)
    grok.require('zope2.View')
    
    # grok.name('view')