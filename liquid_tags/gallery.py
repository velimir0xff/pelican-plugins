"""
Gallery Tag
-----------
This implements a Liquid-style gallery tag for Pelican. It helps to create you
image galleries from flicker photosets.

Syntax
------
{% gallery "photoset_title"  %}

Examples
--------
{% gallery "christmas market" %}

Output
------
<div class="justified-gallery">
    <a href="path/to/image1.jpg">
        <img src="path/to/image1_thumbnail.jpg"/>
    </a>
    <a href="path/to/image2.jpg" title="Just in a dream Place">
        <img src="path/to/image2_thumbnail.jpg"/>
    </a>
    ...
</div>

"""
import re
import flickrapi
from .mdx_liquid_tags import LiquidTags

import logging
logger = logging.getLogger(__name__)

SYNTAX = '{% gallery "photoset_title" %}'
GALLERY_BLOCK_RE = re.compile(r'"(?P<title>[^"]+)"\s*(?P<photos>\[.+\])?')
GALLERY_HTML = """<div class="justified-gallery">{images}</div>"""
IMAGE_LINK = """<a href="{href}" title="{title}" target="_blank">
<img alt="{title}" src="{thumbnail}"/>
</a>"""

def get_user_id(flickr, username):
    userinfo = flickr.people.findByUsername(username=username)
    return userinfo['user']['id']

def find_photoset(flickr, user_id, title):
    response = flickr.photosets.getList(user_id=user_id)
    psets = list(matching_photosets(response['photosets'], title))
    psets.sort(key=lambda it: len(it['title']['_content']))

    if not psets:
        raise ValueError('Can not find photoset with id {}'.format(title))

    return psets[0]

def matching_photosets(photosets, title):
    for pset in photosets['photoset']:
        if re.search(title, pset['title']['_content'], re.IGNORECASE):
            yield pset

def list_photos(flickr, user_id, photoset_id):
    response = flickr.photosets.getPhotos(user_id=user_id, photoset_id=photoset_id)
    return response['photoset']['photo']

def image_url(photo):
    fmt = "https://farm{farm}.staticflickr.com/{server}/{id}_{secret}.jpg"
    return fmt.format(**photo)

def large_image_url(photo):
    fmt = "https://farm{farm}.staticflickr.com/{server}/{id}_{secret}_b.jpg"
    return fmt.format(**photo)

def gen_images_html(flickr, photos):
    for photo in photos:
        href = large_image_url(photo)
        title = photo['title']
        thumbnail = image_url(photo)
        yield IMAGE_LINK.format(href=href, title=title, thumbnail=thumbnail)

def create_html(flickr, photos):
    images = gen_images_html(flickr, photos)
    html = GALLERY_HTML.format(images='\n'.join(images))
    return html

@LiquidTags.register('gallery')
def gallery(preprocessor, tag, markup):
    match = GALLERY_BLOCK_RE.search(markup)
    if not match:
        raise ValueError('Error processing input. '
                         'Expected syntax: {}'.format(SYNTAX))

    matches = match.groupdict()
    logger.debug('matches: %s', matches)
    title = matches['title']
    api_key = preprocessor.configs.getConfig('FLICKR_API_KEY')
    api_secret = preprocessor.configs.getConfig('FLICKR_API_SECRET')
    flickr = flickrapi.FlickrAPI(api_key, api_secret, cache=True,
                                 format='parsed-json')

    username = preprocessor.configs.getConfig('FLICKR_USERNAME')
    user_id = get_user_id(flickr, username)
    photoset = find_photoset(flickr, user_id, title)
    photos = list_photos(flickr, user_id, photoset['id'])
    if matches['photos']:
        photo_names = set(i.lower() for i in eval(matches['photos']))
        photos = filter(lambda p: p['title'].strip().lower() in photo_names, photos)
        if not photos:
            raise ValueError(
                'Can not find any photos with titles: {}'.format(matches['photos']))

    return create_html(flickr, photos)

# ---------------------------------------------------
# This import allows image tag to be a Pelican plugin
from liquid_tags import register
