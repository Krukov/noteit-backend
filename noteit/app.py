#!/usr/bin/python
# -*- coding: utf-8 -*-

import muffin
from .middlewares import baseauth_middleware_factory, token_middleware_factory

app = application = muffin.Application('noteit', CONFIG='config.local')
app._middlewares.extend([token_middleware_factory, baseauth_middleware_factory])


