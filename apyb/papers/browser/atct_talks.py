# -*- coding:utf-8 -*-
from five import grok

from Acquisition import aq_inner

from zope.schema.interfaces import IVocabularyFactory
from zope.component import getMultiAdapter, queryUtility

from Products.ATContentTypes.interfaces import IATTopic



class View(grok.View):
    grok.context(IATTopic)
    grok.require('zope2.View')
    grok.name('atct_talks')
    
    def update(self):
        super(View,self).update()
        context = aq_inner(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        voc_factory = queryUtility(IVocabularyFactory, 
                                   'apyb.papers.talk.rooms')
        self.rooms = voc_factory(self.context)

        portal = self.portal.portal()
        program = portal.restrictedTraverse('2011/programacao/grade-do-evento')
        self.helper = getMultiAdapter((program, self.request), name=u'helper')
    
    def speaker_name(self, speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        helper = self.helper
        speakers_dict = helper.speakers_dict
        results = [speaker for uid,speaker in speakers_dict.items() if uid in speaker_uids]
        return ', '.join([b['name'] for b in results])
    
    def track_info(self, track_uid):
        if track_uid:
            helper = self.helper
            info = helper.track_info(track_uid)
        else:
            info = {'title': 'PythonBrasil[7]',}
        return info

    def show_calendar(self, item):
        location = item.location
        start = item.start
        end = item.end
        return location and start and end

    def location(self, item):
        rooms = self.rooms
        location = item.location
        term = rooms.getTerm(location)
        return term.title

    def date(self, item):
        date = item.start
        return date.strftime('%d/%m')

    def start(self, item):
        start = item.start
        return start.strftime('%H:%M')
