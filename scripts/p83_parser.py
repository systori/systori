import re
import string
from io import BytesIO
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.plaintext.writer import PlaintextWriter


# string translate thing to cleanup the [Langtext]s
tr = str.maketrans(string.whitespace, ' '*len(string.whitespace))

# P83 Tag Praser
# Looks for begin tag, looks for end tag,
# verfies that the begin tag ID matches the end tag id.
def tag_compiler(tag):
    regex = '\#begin\[(?P<tag>'+tag+')\]([0-9]+)\s(?P<content>.*?)\#end\['+tag+'\]\\2\s'
    return re.compile(regex, re.DOTALL)

LV = tag_compiler('LV')
LVInfo = tag_compiler('LVInfo')
LVBereich = tag_compiler('LVBereich')
Position = tag_compiler('Position')
Beschreibung = tag_compiler('Beschreibung')


# P83 Attributes
# Keep returning attributes until we find a # which
# means some other tag has started.
ATTR = re.compile('\[(?P<key>\w+)\](?P<value>.*?)\[end\]\s*(?P<is_last>\#)?', re.DOTALL)
def get_attributes(content):
    for attr in ATTR.finditer(content):
        yield attr.group('key'), attr.group('value')
        if attr.group('is_last'): break

def attr_dict(content):
    return dict(list(get_attributes(content)))

def get_content_attrs(match):
    content = match.group('content')
    attrs = attr_dict(content)
    attrs.update(attr_dict(Beschreibung.search(content).group('content')))
    return content, attrs


def rtf_to_text(value):
    if len(value) == 0: return value
    rtf_doc = Rtf15Reader.read(BytesIO(value.encode('latin_1')))
    txt_doc = BytesIO()
    PlaintextWriter.write(rtf_doc, txt_doc, encoding='latin_1')
    return txt_doc.getvalue().decode('latin_1')


# Build up the structure and convert it into something
# Systori can use...

def parse_p83_file(filename):
    data = open(filename, encoding='latin_1').read()
    content = LV.search(data).group('content')

    project_dict = {
        'attrs': attr_dict(LVInfo.search(content).group('content')),
        'jobs': []
    }

    for _ in LVBereich.finditer(content):

        for job in LVBereich.finditer(_.group('content')):
            job_content, job_attrs = get_content_attrs(job)
            job_dict = {'attrs': job_attrs, 'taskgroups': []}
            job_dict['attrs']['Langtext'] = re.sub("\s\s+", " ", (rtf_to_text(job_dict['attrs']['Langtext'])).translate(tr))
            project_dict['jobs'].append(job_dict)

            for taskgroup in LVBereich.finditer(job_content):
                taskgroup_content, taskgroup_attrs = get_content_attrs(taskgroup)
                taskgroup_dict = {'attrs': taskgroup_attrs, 'tasks': []}
                taskgroup_dict['attrs']['Langtext'] = re.sub("\s\s+", " ", (rtf_to_text(taskgroup_dict['attrs']['Langtext'])).translate(tr))
                job_dict['taskgroups'].append(taskgroup_dict)

                for task in Position.finditer(taskgroup_content):
                    task_content, task_attrs = get_content_attrs(task)
                    task_dict = {'attrs': task_attrs}
                    task_dict['attrs']['Langtext'] = re.sub("\s\s+", " ", (rtf_to_text(task_dict['attrs']['Langtext'])).translate(tr))
                    taskgroup_dict['tasks'].append(task_dict)

    return project_dict


if __name__ == '__main__':
    project = parse_p83_file('gaeb2000_file.p83')

    print("Project:")
    for key, value in project['attrs'].items():
        print(" {}: {}".format(key, value))
    print()

    for job in project['jobs']:
        print("Job:")
        for key, value in job['attrs'].items():
            print(" {}: {}".format(key, value))
        print()

        for taskgroup in job['taskgroups']:
            print("    Task Group:")
            for key, value in taskgroup['attrs'].items():
                print("     {}: {}".format(key, value))
            print()

            for task in taskgroup['tasks']:
                print("      Task:")
                for key, value in task['attrs'].items():
                    print("       {}: {}".format(key, value))
                print()
