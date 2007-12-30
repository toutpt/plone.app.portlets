from StringIO import StringIO

from xml.dom.minidom import parseString

from zope.app.component.hooks import setSite, setHooks
from zope.component import getSiteManager
from zope.component import getUtility

from Products.GenericSetup.testing import DummySetupEnviron

from plone.portlets.interfaces import IPortletType

from plone.app.portlets.exportimport.portlets import PortletsXMLAdapter
from plone.app.portlets.tests.base import PortletsTestCase

class TestExportPortlets(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        sm = getSiteManager(self.portal)
        self.importer = self.exporter = \
          PortletsXMLAdapter(sm, DummySetupEnviron())
    
    def test_extractPortletNode(self):
        node = parseString(_TEST_PORTLET_IMPORT_1).documentElement
        self.importer._initPortletNode(node)
        portlet = getUtility(IPortletType, 'portlets.New')
        node = self.exporter._extractPortletNode('portlets.New', portlet)
        file = StringIO()
        node.writexml(file)
        file.seek(0)
        self.assertEqual("""<portlet title="Foo" addview="portlets.New" description="Foo"><for interface="plone.app.portlets.interfaces.IColumn"/><for interface="plone.app.portlets.interfaces.IDashboard"/></portlet>""", file.read())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExportPortlets))
    return suite

_TEST_PORTLET_IMPORT_1 = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IColumn" />
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""
