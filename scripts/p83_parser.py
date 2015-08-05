import re


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

# Build up the structure and convert it into something
# Systori can use...

data = open('gaeb2000_file.p83', encoding='latin_1').read()
content = LV.search(data).group('content')
project = {
    'attrs': attr_dict(LVInfo.search(content).group('content')),
    'jobs': []
}

for job in LVBereich.finditer(content):
    job_content, job_attrs = get_content_attrs(job)
    print('Job:', job_attrs['Kurztext'])
    print()

    for taskgroup in LVBereich.finditer(job_content):
        taskgroup_content, taskgroup_attrs = get_content_attrs(taskgroup)
        print()
        print(' Task Group:', taskgroup_attrs['Kurztext'])
        for key, value in taskgroup_attrs.items():
            if key in ['Langtext', 'Kurztext', 'Bez']: continue
            print('  {}: {}'.format(key, value))
        print()

        for task in Position.finditer(taskgroup_content):
            task_content, task_attrs = get_content_attrs(task)
            print('   Task:', task_attrs['Kurztext'])
            for key, value in task_attrs.items():
                if key in ['Langtext', 'Kurztext']: continue
                print('     {}: {}'.format(key, value))
            print()
