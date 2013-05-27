# Copyright (c) 2005-2011 Dynamic Solutions Inc. (support@dynamic-solutions.com)
#
# This file is part of DataZoomer.
#
# DataZoomer is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# DataZoomer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Utilities that rely only on standard python libraries"""

import string

norm = string.maketrans('','')
special = string.translate(norm, norm, string.letters + string.digits + ' ')

def trim(text):
    """
        Remove the left most spaces for markdown

        >>> trim('remove right ')
        'remove right'

        >>> trim(' remove left')
        'remove left'

        >>> trim(' remove spaces \\n    from block\\n    of text ')
        'remove spaces\\n   from block\\n   of text'

    """
    n = 0
    for line in text.splitlines():
        if line.isspace():
            continue
        if line.startswith(' '):
            n = len(line) - len(line.lstrip())
            break
    if n:
        lines = []
        for line in text.splitlines():
            lines.append(line[n:].rstrip())
        return '\n'.join(lines)
    else:
        return text.strip()

def name_for(text):
    """Calculates a valid HTML field name given an arbitrary string."""
    return text.replace('*','').replace(' ','_').strip().upper()

def id_for(text):
    """
    Calculates a valid HTML tag id given an arbitrary string.

        >>> id_for('Test 123')
        'test-123'
        >>> id_for('New Record')
        'new-record'
        >>> id_for('New "special" Record')
        'new-special-record'

    """
    return str(text.strip()).translate(norm, special).lower().replace(' ','-')
    return text.replace('*','').replace(' ','-').strip().lower()

def tag_for(tag_text,content='',*args,**keywords):
    """
    Builds an HTML tag.
    
        >>> tag_for('a',href='http://www.google.com')
        '<A HREF="http://www.google.com" />'
    
    """
    tag_type = tag_text.upper()
    singles = ''.join([' %s' % arg.upper() for arg in args])
    attribute_text = ''.join([' %s="%s"' % (key.upper(),keywords[key]) for key in keywords])
    if content or tag_type.lower() in ['textarea']:
        return '<%s%s%s>%s</%s>' % (tag_type,singles,attribute_text,content,tag_type)
    else:
        return '<%s%s%s />' % (tag_type,singles,attribute_text)

def layout_field(label,content,edit=True):
    """
    Layout a field (usually as part of a form).

        >>> layout_field('Name','<input type=text value="John Doe">',True)
        '<div class="field"><div class="field_label">Name</div><div class="field_edit"><input type=text value="John Doe"></div></div>'

        >>> layout_field('Name','John Doe',False)
        '<div class="field"><div class="field_label">Name</div><div class="field_show">John Doe</div></div>'

    """
    if edit:
        tpl = """<div class="field"><div class="field_label">%(label)s</div><div class="field_edit">%(content)s</div></div>"""
    else:
        tpl = """<div class="field"><div class="field_label">%(label)s</div><div class="field_show">%(content)s</div></div>"""
    return tpl % (dict(label=label,content=content))

def kind(o):
    """
    returns a suitable table name for an object based on the object class
    """
    n = []
    for c in o.__class__.__name__:
        if c.isalpha() or c=='_':
            if c.isupper() and len(n):
                n.append('_')
            n.append(c.lower())
    return ''.join(n)

class Storage(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.

        >>> o = Storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'

class Record(Storage):
    """
    A dict with attribute access to items, attributes and properties

        >>> class Foo(Record):
        ...     full = property(lambda a: a.fname + ' ' + a.lname)
        ...
        >>> f = Foo(fname='Joe', lname='Smith')
        >>> f.full
        'Joe Smith'
        >>> f['full']
        'Joe Smith'
        >>> 'The name is %(full)s' % f
        'The name is Joe Smith'
        >>> print f
        Foo
          fname ...............: 'Joe'
          lname ...............: 'Smith'
          full ................: 'Joe Smith'

        >>> f.attributes()
        ['fname', 'lname', 'full']

        >>> class FooBar(Record):
        ...     full = property(lambda a: a.fname + ' ' + a.lname)
        ...
        >>> o = FooBar(a=2)
        >>> kind(o)
        'foo_bar'
        >>> o.a
        2
        >>> o['a']
        2
        >>> o.double = property(lambda o: 2*o.a)
        >>> o.double
        4
        >>> o['double']
        4
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

        >>> class Foo(Record):
        ...     full = property(lambda a: a.fname + ' ' + a.lname)
        ...
        >>> f = Foo(fname='Joe', lname='Smith')
        >>> f.full
        'Joe Smith'
        >>> f['full']
        'Joe Smith'
        >>> 'The name is %(full)s' % f
        'The name is Joe Smith'
        >>> getattr(f,'full')
        'Joe Smith'

        >>> o = Record(a=2)
        >>> o.a
        2
        >>> o['a']
        2
        >>> o.double = property(lambda o: 2*o.a)
        >>> o.double
        4
        >>> o['double']
        4
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

    """

    def attributes(self):
        all_keys = self.keys() + [k for k,v in self.__class__.__dict__.items() if hasattr(v,'__get__')]
        special_keys = 'id', 'key', 'name', 'title', 'description', 'first_name', 'middle_name', 'last_name', 'fname', 'lname'
        result = []
        for key in special_keys:
            if key in all_keys:
                result.append(key)
        for key in sorted(all_keys):
            if not key in special_keys:
                result.append(key)
        return result

    def valid(self):
        return 1

    def __getitem__(self, name):
        try:
            value = dict.__getitem__(self, name)
            if hasattr(value, '__get__'):
                return value.__get__(self)
            else:
                return value
        except KeyError, k:
            try:
                return self.__class__.__dict__[name].__get__(self)
            except KeyError, k:
                raise

    def __str__(self):
        return self.__repr__(pretty=True)

    def __repr__(self, pretty=False):

        name = self.__class__.__name__
        attributes = self.attributes()
        t = []

        items = [(key, self[key]) for key in attributes if not key.startswith('_')]

        if pretty:
            for key, value in items:
                if callable(value):
                    v = value()
                else:
                    v = value
                t.append('  %s %s: %s'  % (key,'.'*(20-len(key[:20])), repr(v)))
            return '\n'.join([name] + t)

        else:
            for key, value in items:
                if callable(value):
                    v = value()
                else:
                    v = value
                t.append((repr(key), repr(v)))
            return '<%s {%s}>' % (name, ', '.join('%s: %s' % (k,v) for k,v in t))



if __name__ == '__main__':
    import doctest
    doctest.testmod()
