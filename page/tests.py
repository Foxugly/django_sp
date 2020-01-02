from django.test import TestCase
from .models import Foo, Bar, Multibar
# Create your tests here.

class BarTestCase(TestCase):
    def setUp(self):
        Bar.objects.create(name="bar1")
        Bar.objects.create(name="bar2")

    def test_bar(self):
        bar1 = Bar.objects.get(name="bar1")
        bar2 = Bar.objects.get(name="bar2")
        self.assertEqual(bar1.name, 'bar1')
        self.assertEqual(bar2.name, 'bar2')

class MultibarTestCase(TestCase):
    def setUp(self):
        Multibar.objects.create(name="multibar1")
        Multibar.objects.create(name="multibar2")

    def test_multibar(self):
        multibar1 = Multibar.objects.get(name="multibar1")
        multibar2 = Multibar.objects.get(name="multibar2")
        self.assertEqual(multibar1.name, 'multibar1')
        self.assertEqual(multibar2.name, 'multibar2')

        
class FooTestCase(TestCase):
    def setUp(self):
        Foo.objects.create(name="foo1", bar=Bar.objects.get(name="bar1"))
        Foo.objects.create(name="foo2", bar=Bar.objects.get(name="bar2"))
        
    def test_foo(self):
        foo1 = Foo.objects.get(name="foo1")
        foo2 = Foo.objects.get(name="foo2")
        self.assertEqual(foo1.bar.name, 'bar1')
        self.assertEqual(foo2.bar.name, 'bar2')
        multibar1 = foo1.multibar.create(name="multibar1")
        multibar1.save()
        multibar2 = foo2.multibar.create(name="multibar2")
        multibar2.save()
        self.assertEqual(foo1.multibar.all()[0].name, 'multibar1')
        self.assertEqual(foo2.multibar.all()[0].name, 'multibar2')
        self.assertEqual(foo1.multibar.get(pk=multibar1.pk), multibar1)
        self.assertEqual(foo2.multibar.get(pk=multibar2.pk), multibar2)
