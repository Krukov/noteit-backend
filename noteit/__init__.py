import muffin

app = application = muffin.Application('noteit', CONFIG='settings.local')

muffin.import_submodules(__name__)