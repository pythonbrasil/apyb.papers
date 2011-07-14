from five import grok
from plone.directives import dexterity, form

from zope import schema

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from z3c.form import group, field
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

from apyb.papers import MessageFactory as _

class ITrack(form.Schema):
    """
    A track within a conference
    """
    
    form.omitted('uid')
    uid = schema.Int(
        title=_(u"uid"),
        required=False,
        )
    #
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Please inform title for this track'),
        required=True,
    )
    #
    description = schema.Text(
        title=_(u"Description"),
        required=True,
        description=_(u"A brief description of this track."),
    )
    
    image = schema.Bytes(
        title=_(u"Track Logo"),
        required=False,
        description=_(u"Upload an image to be used as this track's logo."),
    )



class Track(dexterity.Container):
    grok.implements(ITrack)
    
    # Add your class methods and properties here

    def Title(self):
        return self.title
    
    def UID(self):
        return self.uid
    
    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)

class SampleView(grok.View):
    grok.context(ITrack)
    grok.require('zope2.View')
    
    # grok.name('view')