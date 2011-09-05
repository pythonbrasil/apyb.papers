# -*- coding:utf-8 -*-

from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree
from Products.CMFCore.utils import getToolByName

order = 'apyb.papers.track.talks_order'

def setupAnnotations(context):
    """
    set up the annotations if they haven't been set up
    already. The rest of the functions in here assume that
    this has already been set up
    """
    annotations = IAnnotations(context)
    if not order in annotations:
        annotations[order] = OOBTree()
    
    return annotations


def vote(context, userid=None,talks=None):
    """
    Storage a vote (ordering of talks) for a user in a track
    """
    annotations = IAnnotations(context)

    if not userid:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id
    
    annotations[order][userid] = talks

def getVoters(context):
    """
    Return a list with usernames of voters in here
    """
    annotations = IAnnotations(context)
    votes = annotations[order]
    return [voter for voter in votes.keys()]


def getMyVote(context, userid=None):
    """
    If no user is passed in, the logged in user will be returned
    """
    annotations = IAnnotations(context)
    
    if not userid:
        mtool = getToolByName(context, 'portal_membership')
        userid = mtool.getAuthenticatedMember().id
    
    if userid in annotations[order]:
        return annotations[order][userid]
    
    return None

def rank_talks_in_track(context,close=True):
    ''' Rank all talks for a given track,
        and close voting '''
    wt = getToolByName(context, 'portal_workflow')
    ct = getToolByName(context, 'portal_catalog')
    if not(wt.getInfoFor(context,'review_state') == 'voting'):
        return False
    
    path = '/'.join(context.getPhysicalPath())
    talks_here = dict([(b.UID,b.getId) for b in ct.searchResults(portal_type='apyb.papers.talk',review_state='created',path=path)])
    ntalks = len(talks_here)
    index = 1.0 /  ntalks
    scale = [((ntalks - i) * index)**5 for i in range(0,ntalks+1)]
    
    anno = setupAnnotations(context)[order]
    votes = [(k,v[1],v[0]) for k,v in anno.items()]
    
    talks = {}
    for voter,date,vote in votes:
        vote = list(vote)
        # reverse list
        vote.reverse()
        pos = 0
        while vote:
            talkId = vote.pop()
            if not talkId in talks:
                talks[talkId] = {}
                talks[talkId]['pos'] = [0 for index in range(0,ntalks+1)]
                talks[talkId]['votes'] = []
            talks[talkId]['pos'][pos] = talks[talkId]['pos'][pos] + 1
            # Here we store the human readable position, not the index 
            # (1 instead of 0)
            talks[talkId]['votes'].append((voter,date,pos + 1))
            pos +=1
    
    for talkId in talks:
        oTalk = context[talks_here.get(talkId)]
        oVoteAudit = talks[talkId]['votes']
        oVotePos = talks[talkId]['pos']
        talk_points= sum([scale[i] * oVotePos[i] for i in range(0,len(scale))]) / len(votes)
        talk_votes = oVoteAudit
        oTalk.points = talk_points
        oTalk.votes = talk_votes
        oTalk.reindexCatalog(idxs=['points',])
    if close:
        wt.doActionFor(context,'finish')
    return True

