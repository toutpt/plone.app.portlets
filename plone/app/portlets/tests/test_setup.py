from zope.app.component.hooks import setSite, setHooks
from zope.component import getSiteManager, getUtilitiesFor, getUtility

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IColumnManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletType

from plone.app.portlets.interfaces import ILeftColumn, IRightColumn, IDashboard

from plone.app.portlets.tests.base import PortletsTestCase

class TestProductInstall(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testPortletManagersRegistered(self):
        sm = getSiteManager(self.portal)
        registrations = [r.name for r in sm.registeredUtilities()
                            if IPortletManager == r.provided]
        self.assertEquals(['plone.dashboard1', 'plone.dashboard2',
                           'plone.dashboard3', 'plone.dashboard4',
                           'plone.leftcolumn', 'plone.rightcolumn'],
                           sorted(registrations))

    def testColumnManagersRegistered(self):
        sm = getSiteManager(self.portal)
        registrations = [r.name for r in sm.registeredUtilities()
                            if IColumnManager == r.provided]
        self.assertEquals(['plone.dashboard', 'plone.portlets'],
                          sorted(registrations))
        for c in registrations:
            cmanager = getUtility(IColumnManager,c)
            if c == 'plone.portlet':
                self.assertEqual(['plone.leftcolumn', 'plone.rightcolumn'],
                                 list(cmanager))
            if c == 'plone.dashboard':
                self.assertEqual(['plone.dashboard1', 'plone.dashboard2',
                                  'plone.dashboard3', 'plone.dashboard4'],
                                  list(cmanager))        

    def testInterfaces(self):
        left = getUtility(IPortletManager, 'plone.leftcolumn')
        right = getUtility(IPortletManager, 'plone.rightcolumn')
        dashboard = getUtility(IPortletManager, 'plone.dashboard1')

        self.failUnless(ILeftColumn.providedBy(left))
        self.failUnless(IRightColumn.providedBy(right))
        self.failUnless(IDashboard.providedBy(dashboard))

    def testAssignable(self):
        self.failUnless(ILocalPortletAssignable.providedBy(self.folder))
        self.failUnless(ILocalPortletAssignable.providedBy(self.portal))

    def testPortletTypesRegistered(self):
        portlets = [u[0] for u in getUtilitiesFor(IPortletType)]
        self.failUnless('portlets.Classic' in portlets)
        self.failUnless('portlets.Login' in portlets)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
