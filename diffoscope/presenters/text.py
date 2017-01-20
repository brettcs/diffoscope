# -*- coding: utf-8 -*-
#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017 Chris Lamb <lamby@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import re
import sys
import logging

from diffoscope.diff import color_unified_diff

from .base import Presenter

logger = logging.getLogger(__name__)


class TextPresenter(Presenter):
    PREFIX = u'│ '
    RE_PREFIX = re.compile(r'(^|\n)')

    def __init__(self, print_func, color):
        self.print_func = print_func
        self.color = color

        super().__init__()

    def visit_difference(self, difference):
        if self.depth == 0:
            self.output("--- {}".format(difference.source1))
            self.output("+++ {}".format(difference.source2))
        elif difference.source1 == difference.source2:
            self.output(u"├── {}".format(difference.source1))
        else:
            self.output(u"│   --- {}".format(difference.source1))
            self.output(u"├── +++ {}".format(difference.source2))

        for x in difference.comments:
            self.output(u"│┄ {}".format(x))

        diff = difference.unified_diff

        if diff:
            self.output(color_unified_diff(diff) if self.color else diff, True)

    def output(self, val, raw=False):
        # As an optimisation, output as much as possible in one go to avoid
        # unnecessary splitting, interpolating, etc.
        self.print_func(self.RE_PREFIX.sub(
            r'\1{}'.format(self.PREFIX * (self.depth + 0 if raw else -1)),
            val,
        ))

def output_text(difference, print_func, color=False):
    presenter = TextPresenter(print_func, color)

    try:
        presenter.visit(difference)
    except UnicodeEncodeError:
        logger.critical("Console is unable to print Unicode characters. "
            "Set e.g. PYTHONIOENCODING=utf-8")
        sys.exit(2)
