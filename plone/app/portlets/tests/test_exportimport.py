from StringIO import StringIO

from zope.app.component.hooks import setSite, setHooks
from zope.component import getSiteManager

from xml.dom.minidom import parseString

from Products.GenericSetup.testing import DummySetupEnviron

from plone.portlets.interfaces import IPortletManager
from plone.portlets.manager import PortletManager

from plone.app.portlets.exportimport.portlets import PortletsXMLAdapter
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.tests.utils import FooPortletManager

class PortletsExportImportTestCase(PortletsTestCase):
    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.sm = getSiteManager(self.portal)
        self.importer = self.exporter = PortletsXMLAdapter(self.sm,
          DummySetupEnviron())
    
    def _searchPortletManagerRegistrations(self, name = None):
        results = [r for r in self.sm.registeredUtilities()
          if r.provided.isOrExtends(IPortletManager)]
        if name:
            results = [r for r in results if r.name == name]
        return results
    
    def _node_as_string(self, node):
        file = StringIO()
        node.writexml(file)
        file.seek(0)
        return file.read()
    
class TestImportPortletManagers(PortletsExportImportTestCase):

    def test_initPortletManagerNode_basic(self):
        node = parseString(_XML_BASIC).documentElement
        self.importer._initPortletManagerNode(node)

        manager = queryUtility(IPortletManager, name='plone.foo_column')
        self.failUnless(manager is not None)
        self.assertEqual(PortletManager, manager.__class__)
    
    def test_initPortletManagerNode_customType(self):
        node = parseString(_XML_CUSTOM_TYPE).documentElement
        self.importer._initPortletManagerNode(node)

        manager = queryUtility(IPortletManager, name='plone.foo_column')
        self.failUnless(manager is not None)
        self.failUnless(IColumn.providedBy(manager))
    
    def test_initPortletManagerNode_customClass(self):
        node = parseString(_XML_CUSTOM_CLASS).documentElement
        self.importer._initPortletManagerNode(node)

        manager = queryUtility(IPortletManager, name='plone.foo_column')
        self.failUnless(manager is not None)
        self.assertEqual(FooPortletManager, manager.__class__)
    

class TestExportPortletManagers(PortletsExportImportTestCase):

    def test_extractPortletManagerNode_defaultTypeAndClass(self):
        node = parseString(_XML_BASIC).documentElement
        self.importer._initPortletManagerNode(node)
        results = self._searchPortletManagerRegistrations('plone.foo_column')
        r = results[0]
        node = self.exporter._extractPortletManagerNode(r)
        self.assertEqual('<portletmanager name="plone.foo_column"/>', self._node_as_string(node))

    def test_extractPortletManagerNode_customType(self):
        node = parseString(_XML_CUSTOM_TYPE).documentElement
        self.importer._initPortletManagerNode(node)
        results = self._searchPortletManagerRegistrations('plone.foo_column')
        r = results[0]
        node = self.exporter._extractPortletManagerNode(r)
        self.assertEqual('<portletmanager name="plone.foo_column"  type="plone.app.portlets.interfaces.IColumn"/>', self._node_as_string(node))
    
    def test_extractPortletManagerNode_customClass(self):
        node = parseString(_XML_CUSTOM_CLASS).documentElement
        self.importer._initPortletManagerNode(node)
        results = self._searchPortletManagerRegistrations('plone.foo_column')
        r = results[0]
        node = self.exporter._extractPortletManagerNode(r)
        self.assertEqual('<portletmanager name="plone.foo_column"  class="plone.app.portlets.tests.utils.FooPortletManager"/>', self._node_as_string(node))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImportPortletManagers))
    suite.addTest(makeSuite(TestExportPortletManagers))
    return suite

_XML_BASIC = """<?xml version="1.0"?>
<portletmanager name="plone.foo_column" />
"""

_XML_CUSTOM_TYPE = """<?xml version="1.0"?>
<portletmanager name="plone.foo_column" type="plone.app.portlets.interfaces.IColumn" />
""" 

_XML_CUSTOM_CLASS = """<?xml version="1.0"?>
<portletmanager name="plone.foo_column" class="plone.app.portlets.tests.utils.FooPortletManager" />
"""
