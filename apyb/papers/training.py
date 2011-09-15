# -*- coding:utf-8 -*
from five import grok
from DateTime import DateTime
from Acquisition import aq_inner

from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility

from plone.directives import dexterity, form
from plone.indexer import indexer

from apyb.papers import MessageFactory as _
from apyb.papers.talk import SpeakerSourceBinder
from apyb.papers.talk import SpeakerFieldWidget


class ITraining(form.Schema):
    """
    A training session
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
        description=_(u'Please fill in the name of the speaker. \
                        If no speaker profile was created for this name, \
                        click on Add new speaker'),
        default=[],
        value_type=schema.Choice(title=_(u"Speaker"),
                                 source=SpeakerSourceBinder()),
        required=True,
        )
    #
    title = schema.TextLine(
        title=_(u'Training Title'),
        description=_(u'Inform a training title'),
        required=True,
    )
    #
    form.widget(text='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
    text = schema.Text(
        title=_(u"Training details"),
        required=True,
        description=_(u"A description of this training"),
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
        description=_(u"Which track this training is"),
        vocabulary='apyb.papers.talk.track',
    )
    #
    level = schema.Choice(
        title=_(u"Level"),
        required=True,
        description=_(u"Level of this training"),
        vocabulary='apyb.papers.talk.level',
    )
    #
    iul = schema.Bool(
        title=_(u"Do you allow your image to be used in \
                  post-conference videos?"),
        required=False,
        default=True,
    )
    #
    form.fieldset('allocation',
            label=_(u"Training Allocation"),
            fields=['points', 'votes', 'seats', 'startDate',
                    'endDate', 'location'],
    )
    #
    dexterity.read_permission(points='zope2.View')
    dexterity.write_permission(points='apyb.papers.AllocateTalk')
    form.omitted('points')
    points = schema.Float(
        title = _(u"Points"),
        description = _(u""),
        required = False,
    )
    #
    dexterity.read_permission(votes='zope2.View')
    dexterity.write_permission(votes='apyb.papers.AllocateTalk')
    form.omitted('votes')
    votes = schema.Dict(
        title =_(u"Votes"),
        description = _(u"Votes for this training. \
                        Position is relative to track."),
        required = False,
    )
    #
    dexterity.read_permission(location='zope2.View')
    dexterity.write_permission(location='apyb.papers.AllocateTalk')
    location = schema.Choice(
        title=_(u"Location"),
        required=False,
        description=_(u"Room where this training will be presented"),
        vocabulary='apyb.papers.talk.rooms',
    )
    #
    dexterity.read_permission(seats='zope2.View')
    dexterity.write_permission(seats='apyb.papers.AllocateTalk')
    seats = schema.Int(
        title =_(u"Seats"),
        description = _(u"Available seats to this training."),
        default=1,
        required = False,
    )
    #
    dexterity.read_permission(startDate='zope2.View')
    dexterity.write_permission(startDate='apyb.papers.AllocateTalk')
    #form.widget(startDate='collective.z3cform.datetimewidget.DatetimeWidget')
    startDate = schema.Datetime(
        title=_(u"Start date"),
        required=False,
        description=_(u"Training start date"),
    )
    #
    dexterity.read_permission(endDate='zope2.View')
    dexterity.write_permission(endDate='apyb.papers.AllocateTalk')
    #form.widget(endDate='collective.z3cform.datetimewidget.DatetimeWidget')
    endDate = schema.Datetime(
        title=_(u"End date"),
        required=False,
        description=_(u"Training end date"),
    )
    #
    form.fieldset('material',
            label=_(u"Training materials"),
            fields=['presentation', 'video', 'files'],
    )
    #
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

class Training(dexterity.Container):
    grok.implements(ITraining)
    #
    def Title(self):
        return self.title
    #
    def UID(self):
        return self.uid
    #
    @property
    def uid(self):
        intids = getUtility(IIntIds)
        return intids.getId(self)


@indexer(ITraining)
def startIndexer(obj):
    if obj.startDate is None:
        return None
    return DateTime(obj.startDate.isoformat())
grok.global_adapter(startIndexer, name="start")


@indexer(ITraining)
def endIndexer(obj):
    if obj.endDate is None:
        return None
    return DateTime(obj.endDate.isoformat())
grok.global_adapter(endIndexer, name="end")


class View(dexterity.DisplayForm):
    grok.context(ITraining)
    grok.require('zope2.View')
    #
    def update(self):
        super(View, self).update()
        context = aq_inner(self.context)
        self.context = context
        self._path = '/'.join(context.getPhysicalPath())
        self.state = getMultiAdapter((context, self.request),
                                      name=u'plone_context_state')
        self.tools = getMultiAdapter((context, self.request),
                                      name=u'plone_tools')
        self.portal = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        self._ct = self.tools.catalog()
        self._mt = self.tools.membership()
        self._wt = self.tools.workflow()
        self.member = self.portal.member()
        self.roles_context = self.member.getRolesInContext(context)
        if not self.show_border:
            self.request['disable_border'] = True
    #
    @property
    def show_border(self):
        ''' Is this user allowed to edit this content '''
        return self.state.is_editable()
    #
    def speaker_info(self):
        ''' return information about speakers to this talk '''
        speakers = self.context.speakers
        ct = self._ct
        results = ct.searchResults(portal_type='apyb.papers.speaker',
                                   UID=speakers)
        #
        return results
