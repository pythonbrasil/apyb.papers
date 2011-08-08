# -*- coding:utf-8 -*-
from five import grok

from Acquisition import aq_inner
from zope.component import getMultiAdapter

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
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.is_anonymous = self.portal.anonymous()
        self.member = self.portal.member()
        roles_context = self.member.getRolesInContext(context)
        if not self.show_border:
            self.request['disable_border'] = True
    
    
    @property
    def can_submit(self):
        ''' This user can submit a talk in here'''
        context = self.context
        return self._mt.checkPermission('apyb.papers: Add Talk',context)
    
    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()
    
    def speaker_name(self,speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        ct = self._ct
        results = ct.searchResults(portal_type='apyb.papers.speaker',UID=speaker_uids)
        return ', '.join([b.Title for b in results])
    
    def tracks(self):
        ''' Return a list of tracks in here '''
        results = self._ct.searchResults(portal_type='apyb.papers.track', 
                                         path=self._path,
                                         sort_on='getObjPositionInParent')
        return results
    
    def speakers(self):
        ''' Return a list of speakers in here '''
        results = self._ct.searchResults(portal_type='apyb.papers.speaker',
                                         path=self._path,        
                                         sort_on='sortable_title')
        return results
    
    def talks(self):
        ''' Return a list of talks in here '''
        results = self._ct.searchResults(portal_type='apyb.papers.talk', 
                                         path=self._path,
                                         sort_on='sortable_title')
        return results
    
    def my_talks(self):
        ''' Return a list of my talks '''
        results = self._ct.searchResults(portal_type='apyb.papers.talk', 
                                         path=self._path,
                                         Creator=self.member.getUserName(),
                                         sort_on='sortable_title')
        return results
    
    def my_profiles(self):
        ''' Return a list of my speaker profiles '''
        results = self._ct.searchResults(portal_type='apyb.papers.speaker', 
                                         path=self._path,
                                         Creator=self.member.getUserName(),
                                         sort_on='sortable_title')
        return results
    
    def last_talks(self):
        ''' Return a list of the last 5 talks in here '''
        results = self._ct.searchResults(portal_type='apyb.papers.talk', 
                                         path=self._path,
                                         sort_on='created',
                                         sort_order='reverse',
                                         sort_limit=5,)
        return results[:5]
    
class Speakers(grok.View):
    grok.context(IProgram)
    grok.require('zope2.View')
    grok.name('speakers')
    
    def update(self):
        super(View,self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self.member = self.portal.member()
        roles_context = self.member.getRolesInContext(context)
        if not show_border:
            self.request['disable_border'] = True
    
    
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
    
    

  