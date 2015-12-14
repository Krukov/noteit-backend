#!/usr/bin/python
# -*- coding: utf-8 -*-

import muffin


app = application = muffin.Application('noteit', CONFIG='settings.local')
muffin.import_submodules(__name__)
