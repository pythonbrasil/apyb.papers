# -*- coding:utf-8 -*-
import json
from datetime import datetime

from zope.publisher.interfaces import IPublishTraverse

from five import grok
from plone.directives import dexterity, form

from random import shuffle

from Acquisition import aq_inner
from Acquisition import aq_parent

from zope.schema.interfaces import IVocabularyFactory
from zope.component import getMultiAdapter, queryUtility

from plone.namedfile.field import NamedImage

from zope import schema

from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from Products.statusmessages.interfaces import IStatusMessage

from apyb.papers import ordering

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
        super(View, self).update()
        context = aq_inner(self.context)
        program = aq_parent(context)
        self.annotations = ordering.setupAnnotations(self.context)
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                      name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                      name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self.helper = getMultiAdapter((program, self.request),
                                      name=u'helper')
        voc_factory = queryUtility(IVocabularyFactory,
                                   'apyb.papers.talk.rooms')
        self.rooms = voc_factory(self.context)
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self.member = self.portal.member()
        self.member_id = self.member.id
        if not self.show_border:
            self.request['disable_border'] = True

    @property
    def vocabs(self):
        if not hasattr(self, "_vocabs"):
            vocabs = {}
            vocabs['languages'] = queryUtility(IVocabularyFactory,
                                               'apyb.papers.languages')
            vocabs['level'] = queryUtility(IVocabularyFactory,
                                           'apyb.papers.talk.level')
            self._vocabs = dict((key, value(self))
                                 for key, value in vocabs.items())
        return self._vocabs

    def speakers(self, speaker_uids):
        ''' Given a list os uids,
            we return a list of dicts with speakers data
        '''
        speaker_image = self.helper.speaker_image_from_brain
        ct = self._ct
        brains = ct.searchResults(portal_type='apyb.papers.speaker',
                                  UID=speaker_uids)
        speakers = [{'name': b.Title,
                     'organization': b.organization,
                     'bio': b.Description,
                     'country': b.country,
                     'state': b.state,
                     'city': b.city,
                     'image_url': speaker_image(b),
                     'url': b.getURL(),
                     'json_url': '%s/json' % b.getURL(),
                     }
                    for b in brains]
        return speakers

    def speaker_name(self, speaker_uids):
        ''' Given a list os uids, we return a string with speakers names '''
        speakers = self.speakers(speaker_uids)
        return ', '.join([b['name'] for b in speakers])

    @property
    def can_submit(self):
        ''' This user can submit a talk in here'''
        context = self.context
        return self._mt.checkPermission('apyb.papers: Add Talk', context)

    @property
    def can_organize(self):
        ''' This user can organize talks in this track'''
        context = self.context
        return self._mt.checkPermission('apyb.papers: Organize Talk', context)

    @property
    def can_view_voters(self):
        ''' This user can view who voted here'''
        context = self.context
        return self._mt.checkPermission('apyb.papers: View Votes', context)

    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()

    def memberdata(self, userid=None):
        ''' Return memberdata for a userid '''
        memberdata = self._mt.getMemberById(userid)
        if memberdata:
            return memberdata.getProperty('fullname', userid) or userid
        else:
            return userid

    def voters(self):
        ''' Return a list of voters in here '''
        voters = ordering.getVoters(self.context)
        voters = [(self.memberdata(voter), voter) for voter in voters]
        voters.sort()
        return voters

    def confirmed_talks(self, **kw):
        ''' Return a list of talks in here '''
        kw['sort_on'] = 'points'
        kw['sort_order'] = 'reverse'
        kw['review_state'] = 'confirmed'
        results = self.talks(**kw)
        return results

    def ordered_talks(self, **kw):
        ''' Return a list of talks in here '''
        kw['sort_on'] = 'points'
        kw['sort_order'] = 'reverse'
        results = self.talks(**kw)
        return results

    def talks(self, **kw):
        ''' Return a list of talks in here '''
        kw['portal_type'] ='apyb.papers.talk'
        kw['path'] =self._path
        if not 'sort_on' in kw:
            kw['sort_on'] = 'sortable_title'
        results = self._ct.searchResults(**kw)
        return results


class TalksView(View):
    grok.name('talks')


class JSONView(View):
    grok.name('json')

    template = None

    def location(self, value):
        rooms = self.rooms
        location = value
        try:
            term = rooms.getTerm(location)
        except LookupError:
            return 'PythonBrasil[7]'
        return term.title

    def talks(self):
        ''' Return a list of talks in here '''
        brains = super(JSONView, self).talks()
        talks = []
        for brain in brains:
            talk = {}
            talk['creation_date'] = brain.CreationDate
            talk['title'] = brain.Title
            talk['description'] = brain.Description
            talk['track'] = self.context.title
            talk['speakers'] = self.speakers(brain.speakers)
            talk['language'] = brain.language
            talk['state'] = brain.review_state
            if talk['state'] == 'confirmed':
                talk['talk_location'] = self.location(brain.location)
                talk['talk_start'] = brain.start.asdatetime().isoformat()
                talk['talk_end'] = brain.end.asdatetime().isoformat()
            talk['points'] = brain.points or 0.0
            talk['url'] = '%s' % brain.getURL()
            talk['json_url'] = '%s/json' % brain.getURL()
            talks.append(talk)
        return talks

    def render(self):
        talks = self.talks()
        data = {'talks': talks}
        data['url'] = self.context.absolute_url()
        data['title'] = self.context.title
        data['description'] = self.context.description
        data['total_talks'] = len(talks)
        data['total_votes'] = len(self.voters())
        self.request.response.setHeader('Content-Type',
                                        'application/json;charset=utf-8')
        return json.dumps(data,
                          encoding='utf-8',
                          ensure_ascii=False)


class OrganizeView(View):
    grok.context(ITrack)
    grok.name('order-talks')
    grok.require('apyb.papers.OrganizeTalk')

    def _talks(self, **kw):
        ''' Return a randomized list of talks '''
        kw['review_state'] = 'created'
        talks = super(OrganizeView, self).talks(**kw)
        talks = dict([(talk.UID, talk) for talk in talks])
        return talks

    def talks(self, **kw):
        ''' Return a randomized list of talks '''
        talks = self._talks(**kw)
        vote = self.my_vote()
        if vote:
            order = vote.get('order')
            talks = [talks[UID] for UID in order]
        else:
            talks = [talk for talk in talks.values()]
            shuffle(talks)
        return talks

    def talk_metadata(self, brain=None):
        metadata = []
        voc = self.vocabs
        if brain:
            metadata.append(voc['level'].getTerm(brain.level).title)
            metadata.append(voc['languages'].getTerm(brain.language).title)
        return ' / '.join(metadata)

    def process_form(self):
        ''' Process data sent by the user '''
        talk_uids = self.request.form.get('talk_uid', [])
        vote_order = tuple([int(uid) for uid in talk_uids])
        vote_date = datetime.now()
        vote = (vote_order, vote_date)
        return vote

    def my_vote(self):
        ''' Get my vote from annotation storage '''
        member_id = self.member_id
        vote = ordering.getMyVote(self.context, userid=member_id)
        if vote:
            vote_order, vote_date = vote
            return {'order': vote_order, 'date': vote_date}
        else:
            return None

    def update(self):
        super(OrganizeView, self).update()
        messages = IStatusMessage(self.request)

        # Remove Portlets
        self.request['disable_plone.leftcolumn']=1
        self.request['disable_plone.rightcolumn']=1

        if 'form.submitted' in self.request.form:
            vote = self.process_form()
            ordering.vote(self.context, self.member_id, vote)
            messages.addStatusMessage(_(u"Your vote was computed"),
                                      type="info")
        elif self.my_vote():
            messages.addStatusMessage(_(u"You already voted in this track"),
                                      type="info")


class VoteView(OrganizeView):
    grok.context(ITrack)
    grok.implements(IPublishTraverse)
    grok.name('vote')
    grok.require('apyb.papers.ViewVotes')

    email = None

    def publishTraverse(self, request, name):
        self.email = name
        return self

    def _talks(self, **kw):
        ''' Return a randomized list of talks '''
        talks = super(OrganizeView, self).talks(**kw)
        talks = dict([(talk.UID, talk) for talk in talks])
        return talks

    def my_vote(self):
        ''' Get a vote from annotation storage '''
        member_id = self.email
        vote = ordering.getMyVote(self.context, userid=member_id)
        if vote:
            vote_order, vote_date = vote
            return {'order': vote_order, 'date': vote_date}
        else:
            return None
