from mistletoe import Document, HTMLRenderer
from autolink import linkify
from bs4 import BeautifulSoup
import bleach

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
def blank_nofollow_noopener_noreferrer(html) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for link in soup.find_all('a'):
        link.attrs['target'] = "_blank"

        link.attrs['rel'] = "nofollow noopener noreferrer"

    return str(soup)

def render(text) -> str:
    _rendered = ""

    with HTMLRenderer() as renderer:
        _rendered = renderer.render(Document(text))

    _rendered = linkify(_rendered)

    _rendered = blank_nofollow_noopener_noreferrer(_rendered)

    _rendered = bleach.clean(_rendered, tags = ALLOWED_TAGS, attributes = ALLOWED_ATTRS, protocols = ALLOWED_PROTOCOLS)

    return _rendered
