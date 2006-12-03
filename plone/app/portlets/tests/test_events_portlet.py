from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import events
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase

class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        self.assertEquals(portlet.addview, 'portlets.Events')

    def testInterfaces(self):
        portlet = events.Assignment(count=5)
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        adding = getMultiAdapter((mapping, request,), name='+')
        addview = getMultiAdapter((adding, request), name=portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], events.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = events.Assignment(count=5)
        editview = getMultiAdapter((mapping['foo'], request), name='edit.html')
        self.failUnless(isinstance(editview, events.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = events.Assignment(count=5)

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, events.Renderer))

class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or events.Assignment(template='portlet_recent', macro='portlet')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_published_events(self):
        r = self.renderer(assignment=events.Assignment(count=5))
        self.assertEquals(0, len(r.published_events()))

    def test_all_events_link(self):
        r = self.renderer(assignment=events.Assignment(count=5))
        self.failUnless(r.all_events_link().endswith('/events'))
        self.portal._delObject('events')
        r = self.renderer(assignment=events.Assignment(count=5))
        self.failUnless(r.all_events_link().endswith('/events_listing'))
        
    def test_prev_events_link(self):
        r = self.renderer(assignment=events.Assignment(count=5))
        self.failUnless(r.prev_events_link().endswith('/events/previous'))
        self.portal._delObject('events')
        r = self.renderer(assignment=events.Assignment(count=5))
        self.assertEquals(None, r.prev_events_link())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite