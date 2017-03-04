import io
import textwrap
from pathlib import Path

from lxml import etree

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from systori.apps.project.gaeb.convert import Import, Export
from systori.apps.project.gaeb.structure import GAEBStructure, GAEBStructureField
from systori.apps.project.models import Project
from systori.apps.project.factories import ProjectFactory
from systori.apps.task.models import Job, Group, Task, LineItem
from systori.apps.task.factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory


class GAEBExportTests(SimpleTestCase):

    def assertXML(self, expected, element):
        expected = textwrap.dedent(expected)
        actual = etree.tostring(element, pretty_print=True).decode()
        self.assertEqual(expected, actual)

    def test_empty_project(self):
        project = ProjectFactory.build(name='prj')
        self.assertXML("""\
            <GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
              <PrjInfo>
                <LblPrj>prj</LblPrj>
              </PrjInfo>
              <Award>
                <BoQ>
                  <BoQBody/>
                </BoQ>
              </Award>
            </GAEB>
            """,
            Export().project(project)
        )

    def test_full_project(self):
        project = ProjectFactory.build(name='prj')
        job = JobFactory.build(order=1, project=project, name='job')
        job.job = job
        group = GroupFactory.build(order=1, parent=job, name='section')
        job._prefetched_objects_cache = {'groups': [group]}
        task = TaskFactory.build(order=1, group=group, name='task')
        group._prefetched_objects_cache = {'groups': [], 'tasks': [task]}
        self.maxDiff = None
        self.assertXML("""\
            <GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
              <PrjInfo>
                <LblPrj>prj</LblPrj>
              </PrjInfo>
              <Award>
                <BoQ>
                  <BoQBody>
                    <BoQCtgy>
                      <LblTx>job</LblTx>
                      <BoQBody>
                        <BoQCtgy>
                          <LblTx>section</LblTx>
                          <BoQBody>
                            <Itemlist>
                              <Item>
                                <Qty>0.00</Qty>
                                <QU></QU>
                                <Description>
                                  <CompleteText>
                                    <OutlineText>
                                      <OutlTxt>
                                        <TextOutlTxt>task</TextOutlTxt>
                                      </OutlTxt>
                                    </OutlineText>
                                    <DetailTxt>
                                      <Text></Text>
                                    </DetailTxt>
                                  </CompleteText>
                                </Description>
                              </Item>
                            </Itemlist>
                          </BoQBody>
                        </BoQCtgy>
                      </BoQBody>
                    </BoQCtgy>
                  </BoQBody>
                </BoQ>
              </Award>
            </GAEB>
            """,
            Export().project(project, [job])
        )

    def test_job(self):
        project = ProjectFactory.build()
        job = JobFactory.build(order=1, project=project, name='the italian job')
        job.job = job
        self.assertXML("""\
            <BoQCtgy xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
              <LblTx>the italian job</LblTx>
              <BoQBody/>
            </BoQCtgy>
            """,
            Export().group(job)
        )

    def test_group(self):
        project = ProjectFactory.build()
        job = JobFactory.build(order=1, project=project)
        job.job = job
        group = GroupFactory.build(order=1, parent=job, name='section')
        group2 = GroupFactory.build(order=1, parent=group, name='sub-section')
        group._prefetched_objects_cache = {'groups': [group2]}
        self.assertXML("""\
            <BoQCtgy xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
              <LblTx>section</LblTx>
              <BoQBody>
                <BoQCtgy>
                  <LblTx>sub-section</LblTx>
                  <BoQBody/>
                </BoQCtgy>
              </BoQBody>
            </BoQCtgy>
            """,
            Export().group(group)
        )

    def test_task(self):
        project = ProjectFactory.build()
        job = JobFactory.build(order=1, project=project)
        job.job = job
        group = GroupFactory.build(order=1, parent=job)

        task = TaskFactory.build(order=1, group=group, name='task')
        self.assertXML("""\
            <Item xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
              <Qty>0.00</Qty>
              <QU></QU>
              <Description>
                <CompleteText>
                  <OutlineText>
                    <OutlTxt>
                      <TextOutlTxt>task</TextOutlTxt>
                    </OutlTxt>
                  </OutlineText>
                  <DetailTxt>
                    <Text></Text>
                  </DetailTxt>
                </CompleteText>
              </Description>
            </Item>
            """,
            Export().task(task)
        )

        task = TaskFactory.build(order=1, group=group, name='optional', is_provisional=True)
        self.assertXML("""\
            <Item xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
              <Qty>0.00</Qty>
              <QU></QU>
              <Description>
                <CompleteText>
                  <OutlineText>
                    <OutlTxt>
                      <TextOutlTxt>optional</TextOutlTxt>
                    </OutlTxt>
                  </OutlineText>
                  <DetailTxt>
                    <Text></Text>
                  </DetailTxt>
                </CompleteText>
              </Description>
              <Provis/>
            </Item>
            """,
            Export().task(task)
        )

        task = TaskFactory.build(order=1, group=group, name='alternate',
                                 variant_group=100, variant_serial=1)
        self.assertXML("""\
            <Item xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">
              <Qty>0.00</Qty>
              <QU></QU>
              <Description>
                <CompleteText>
                  <OutlineText>
                    <OutlTxt>
                      <TextOutlTxt>alternate</TextOutlTxt>
                    </OutlTxt>
                  </OutlineText>
                  <DetailTxt>
                    <Text></Text>
                  </DetailTxt>
                </CompleteText>
              </Description>
              <ALNGroupNo>100</ALNGroupNo>
              <ALNSerNo>1</ALNSerNo>
            </Item>
            """,
            Export().task(task)
        )


def get_test_data_path(name):
    return Path(Path(__file__).parent / 'test_data' / name)


class GAEBImportTests(SimpleTestCase):

    def parse(self, xml):
        stream = io.StringIO(
            '<GAEB xmlns="http://www.gaeb.de/GAEB_DA_XML/200407">{}</GAEB>'
            .format(xml)
        )
        stream.name = 'test-file.x83'
        return Import().parse(stream)

    def test_bad_file(self):
        self.assertEqual(
            ["File 'test-file.x83' can't be imported. Please contact support."],
            self.parse('<WTF?>').form.non_field_errors()
        )

    def test_simplest_possible_xml(self):
        self.assertEqual(
            'Leaning Tower of Pisa Foundation Work',
            self.parse("""
            <PrjInfo>
            <LblPrj>Leaning Tower of Pisa Foundation Work</LblPrj>
            </PrjInfo>
            <Award><BoQ><BoQBody>
            </BoQBody></BoQ></Award>
            """).project.name
        )

    def test_gaeb_file(self):
        path = get_test_data_path('gaeb.x83')
        parser = Import().parse(path.open())
        self.assertEqual(parser.project.name, '7030 Herschelbad')
        self.assertEqual(len(parser.objects), 19)
        job, group, task = parser.objects[:3]
        self.assertTrue(job, Job)
        self.assertTrue(job.name, 'Halle 2 und 3')
        self.assertTrue(isinstance(group, Group))
        self.assertTrue(group.name, 'Baustelleneinrichtung')
        self.assertTrue(isinstance(task, Task))
        self.assertTrue(task.name, 'Baustelleneinrichtung')

    def test_lv_zimmermann_file(self):
        path = get_test_data_path('lv_zimmermann.x83')
        parser = Import().parse(path.open())
        self.assertEqual(len(parser.objects), 135)


class GAEBImportExportTests(SimpleTestCase):

    def test_round_trip(self):
        project = ProjectFactory.build(name='prj')
        job = JobFactory.build(order=1, project=project, name='job')
        job.job = job
        group = GroupFactory.build(order=1, parent=job, name='section')
        job._prefetched_objects_cache = {'groups': [group]}
        task = TaskFactory.build(order=1, group=group, name='task')
        group._prefetched_objects_cache = {'groups': [], 'tasks': [task]}

        root = Export().project(project, [job])
        xml = etree.tostring(root, pretty_print=True).decode()

        parser = Import().parse(io.StringIO(xml))
        project2 = parser.project
        job2, group2, task2 = parser.objects

        self.assertEqual(project.name, project2.name)
        self.assertEqual(job.name, job2.name)
        self.assertEqual(group.name, group2.name)
        self.assertEqual(task.name, task2.name)


class GAEBStructureTests(SimpleTestCase):

    def test_task_formatting(self):
        struct = GAEBStructure("9.01.02.0009")
        self.assertEqual('0001', struct.format_task(1))
        self.assertEqual('12345', struct.format_task(12345))

    def test_group_formatting(self):
        struct = GAEBStructure("9.000.00.0000")
        self.assertEqual('1', struct.format_group(1, 0))
        self.assertEqual('099', struct.format_group(99, 1))
        self.assertEqual('99', struct.format_group(99, 2))

    def test_is_valid_depth(self):
        struct = GAEBStructure("9.000.00.0000")
        self.assertEqual(struct.is_valid_depth(-1), False)
        self.assertEqual(struct.is_valid_depth(0), True)
        self.assertEqual(struct.is_valid_depth(1), True)
        self.assertEqual(struct.is_valid_depth(2), True)
        self.assertEqual(struct.is_valid_depth(3), False)
        self.assertEqual(struct.is_valid_depth(4), False)

    def test_depth(self):
        gaeb = GAEBStructure
        self.assertEqual(gaeb('0.0').maximum_depth, 0)
        self.assertEqual(gaeb('0.0.0').maximum_depth, 1)
        self.assertEqual(gaeb('0.0.0.0').maximum_depth, 2)


class GAEBStructureFieldTests(SimpleTestCase):

    def test_valid(self):
        GAEBStructureField().clean('0.0', None)
        GAEBStructureField().clean('01.0001.0001.001.0.0', None)

    def test_empty(self):
        with self.assertRaisesMessage(ValidationError, 'cannot be blank'):
            GAEBStructureField().clean('', None)

    def test_too_short(self):
        with self.assertRaisesMessage(ValidationError, 'outside the allowed hierarchy'):
            GAEBStructureField().clean('0', None)

    def test_too_long(self):
        with self.assertRaisesMessage(ValidationError, 'outside the allowed hierarchy'):
            GAEBStructureField().clean('01.0001.0001.001.0.0.0', None)

    def test_depth_field(self):

        project = Project(structure='01.01.001')
        self.assertEquals(project.structure.pattern, '01.01.001')
        self.assertEquals(project.structure_depth, 1)

        # setting `structure` automatically updates `structure_depth`
        project.structure = '01.01.01.001'
        self.assertEquals(project.structure_depth, 2)

        # structure str automatically get converted to GAEBStructure
        self.assertIsInstance(project.structure, GAEBStructure)

        # directly setting `structure_depth` is a no-op
        project.structure_depth = 99
        self.assertEquals(project.structure_depth, 2)
