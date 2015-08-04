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
def get_attributes(contents):
    for attr in ATTR.finditer(contents):
        yield attr.group('key'), attr.group('value')
        if attr.group('is_last'): break

def attr_dict(contents):
    return dict(list(get_attributes(contents)))


# Build up the structure and convert it into something
# Systori can use...

def descend(contents):
    for level in LVBereich.finditer(contents):
        inner = level.group('content')
        for attr in get_attributes(inner):
            print(attr)
        descend(inner)

data = open('gaeb2000_file.p83', encoding='latin_1').read()
content = LV.search(data).group('content')
project = {
    'attrs': attr_dict(LVInfo.search(content).group('content')),
    'levels': descend(content)
}

print(project['attrs'])
