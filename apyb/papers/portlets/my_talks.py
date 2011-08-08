# -*- coding:utf-8 -*-

from five import grok
from plone.portlets.interfaces import IPortletDataProvider
from zope.component import getMultiAdapter
from zope.interface import implements
from zope import schema

from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.navigation.root import getNavigationRootObject

from apyb.papers import MessageFactory as _
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base

class IMyTalksPortlet(IPortletDataProvider):
    ''' List talks for this user '''


class Assignment(base.Assignment):
    implements(IMyTalksPortlet)
    
    title = _(u'My Talks')


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('my_talks.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.navigation_root_url = self.portal_state.navigation_root_url()
        self.portal = self.portal_state.portal()
        self.navigation_root_path = self.portal_state.navigation_root_path()
        self.navigation_root_object = getNavigationRootObject(self.context, self.portal)
    
    def render(self):
        return self._template()
    
    @property
    def available(self):
        return len(self._data())
    
    def talks(self):
        ''' List available talks for the logged in user '''
        return self._data()
    
    def _data(self):
        member = self.portal_state.member()
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        path = self.navigation_root_path
        return catalog(portal_type='apyb.papers.talk',
                       path=path,
                       Creator=member.getUserName(),
                       sort_on='sortable_title')
    
    def review_state(self,value):
        ''' A key to value method '''
        states = {'created':_('Created'),
                  'accepted':_('Accepted'),
                  'rejected':_('Rejected'),
                  'confirmed':_('Confirmed'),
                  'cancelled':_('Cancelled'),}
        return states.get(value,value)
    
class AddForm(base.NullAddForm):
    
    def create(self):
        return Assignment()
