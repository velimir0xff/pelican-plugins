from pelican import signals

def patch_author(generator):
    settings = generator.settings
    author = generator.author

    author_info = settings['AUTHORS'][author.name.lower()]
    for name, value in author_info.iteritems():
        if hasattr(author, name):
            continue
        setattr(author, name, value)

def register():
    signals.content_object_init.connect(patch_author)
