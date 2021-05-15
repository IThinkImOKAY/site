from mistletoe import Document, HTMLRenderer
from bleach.sanitizer import Cleaner
from bleach.linkifier import LinkifyFilter
from functools import partial

ALLOWED_TAGS = [
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'p',
    'a',
    'b',
    'strong',
    'i',
    'ul',
    'ol',
    'li',
    'br',
    'blockquote',
    'hr',
    'em',
    'code',
    'pre'
]

ALLOWED_ATTRS = {
    'a': ['href', 'target', 'rel']
}

ALLOWED_PROTOCOLS = [
    'http',
    'https'
]

# add target="_blank" and ref="nofollow noopener noreferrer" to outgoing links
def blank_nofollow_noopener_noreferrer(attrs, new = False) -> str:
    attrs[(None, 'target')] = "_blank"
    attrs[(None, 'rel')] = "nofollow noopener noreferrer"

    return attrs

cleaner = Cleaner(tags = ALLOWED_TAGS,
    attributes = ALLOWED_ATTRS,
    protocols = ALLOWED_PROTOCOLS,
    filters = [partial(LinkifyFilter, callbacks = [blank_nofollow_noopener_noreferrer], skip_tags = ['pre'])]
)

def render(text) -> str:
    _rendered = ""

    with HTMLRenderer() as renderer:
        _rendered = renderer.render(Document(text))

    _rendered = cleaner.clean(_rendered)

    return _rendered
