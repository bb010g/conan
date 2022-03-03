from collections import namedtuple
import re

class PkgConfigVariable(namedtuple("PkgConfigVariable", ["key", "value"])):
    def __str__(self):
        return "{}={}".format(self.key, self.value)

class PkgConfigProperty(namedtuple("PkgConfigProperty", ["keyword", "value"])):
    def __str__(self):
        return ""

class PkgConfigLine(namedtuple("PkgConfigLine", ["value", "comment"])):
    @classmethod
    def parse(cls, line):
        # re.search('^(?P<key>(?:[\w.]+(?<![_.]))?)(?P<key_whitespace>\s*)(?:(?P<op>.)(?P<op_whitespace>\s*)(?P<value>(?:.+(?<!\s))?)(?P<value_whitespace>\s*))?$',
                  line)
        value = None
        comment = None
        return PkgConfigLine(value, comment)

    def __str__(self):
        value = "" if self.value is None else self.value
        comment = "" if self.comment is None else self.comment
        return "{}{}".format(value, comment)

class PkgConfigPkg:
    _valid_keywords = {
        "name": "Name",
        "version": "Version",
        "description": "Description",
        "url": "Url",
        "requires": "Requires",
        "requires.private": "Requires.private",
        "conflicts": "Conflicts",
        "provides": "Provides",
        "cflags": "Cflags",
        "cflags.private": "Cflags.private",
        "libs": "Libs",
        "libs.private": "Libs.private",
    }

    def __init__(self, *, keywords=None, variables=None):
        self.keywords = [] if keywords is None else keywords
        for keyword_name, keyword_value in keywords:
            self.set_keyword(name=keyword_name, value=keyword_value)
        self.variables = [] if variables is None else variables

    def set_keyword(self, name, value):
        name = name.lower()
        self._valid_keywords[name]
        if value is None:
            return self.keywords.pop(name, None)
        else:
            previous_value = self.keywords.get(name, None)
            self.keywords[name] = value
            return previous_value

    def get_keyword(self, name):
        name = name.lower()
        self._valid_keywords[name]
        return self.keywords.get(name, None)

    def set_variable(self, name, value):
        if value is None:
            return self.variables.pop(name, None)
        else:
            previous_value = self.variables.get(name, None)
            self.variables[name] = value
            return previous_value

    def get_variable(self, name):
        return self.keywords.get(name, None)

    name = _keyword_property("name")
    version = _keyword_property("version")
    description = _keyword_property("description")
    url = _keyword_property("url")
    requires = _keyword_property("requires")
    requires_private = _keyword_property("requires.private")
    conflicts = _keyword_property("conflicts")
    provides = _keyword_property("provides")
    cflags = _keyword_property("cflags")
    cflags_private = _keyword_property("cflags.private")
    libs = _keyword_property("libs")
    libs_private = _keyword_property("libs.private")

    def content(self):
        context = {
            "_valid_keywords": self._valid_keywords,
            "keywords": self.keywords,
            "variables": self.variables,
        }

        template = Template(_get_pkgconfig_pkg_pc_file_template(), trim_blocks=True,
                            lstrip_blocks=True, undefined=StrictUndefined)
        return template.render(context)
