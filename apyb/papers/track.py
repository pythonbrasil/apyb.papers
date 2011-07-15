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
    
    image = NamedImage(
        title=_(u"Track Logo"),
        required=False,
        description=_(u"Upload an image to be used as this track's logo."),
    )



class Track(dexterity.Container):
    grok.implements(ITrack)
    
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
    grok.context(ITrack)
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
    
    
    def speaker_name(self,speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        ct = self._ct
        results = ct.searchResults(portal_type='apyb.papers.speaker',UID=speaker_uids)
        return ', '.join([b.Title for b in results])
    
    @property
    def can_submit(self):
        ''' This user can submit a talk in here'''
        context = self.context
        return self._mt.checkPermission('apyb.papers: Add Talk',context)
    
    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()
    
    def talks(self):
        ''' Return a list of talks in here '''
        results = self._ct.searchResults(portal_type='apyb.papers.talk', 
                                         path=self._path,
                                         sort_on='sortable_title')
        return results
    
