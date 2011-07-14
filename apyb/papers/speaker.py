# -*- coding:utf-8 -*-
from five import grok
from plone.directives import dexterity, form

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
    
    image = schema.Bytes(
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
    
    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)
    
class SampleView(grok.View):
    grok.context(ISpeaker)
    grok.require('zope2.View')
    
    # grok.name('view')