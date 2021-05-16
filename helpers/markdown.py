from mistletoe import Document, HTMLRenderer
from mistletoe.span_token import SpanToken
from bleach.sanitizer import Cleaner
from bleach.linkifier import LinkifyFilter
from functools import partial
import re

from .get import *

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
    'pre',
    'del'
]

ALLOWED_ATTRS = {
    'a': ['href', 'rel']
}

ALLOWED_PROTOCOLS = [
    'http',
    'https'
]

class PostMention(SpanToken):
    pattern = re.compile(r"\+\+([0-9]{1,10})")
    target_post_id = ""
    precedence = 6

    def __init__(self, match):
        self.target_post_id = match.group(1)

class BoardMention(SpanToken):
    pattern = re.compile(r"\+\+\+([a-z]{1,5})/?")
    target_board_name = ""
    precedence = 6

    def __init__(self, match):
        self.target_board_name = match.group(1)

class OPMention(SpanToken):
    pattern = re.compile(r"\+\+([oO][pP])")
    precedence = 6

    def __init__(self, match):
        self.target = match.group(1)

class CustomRenderer(HTMLRenderer):

    # post parent
    context = None

    def __init__(self, **kwargs):
        if 'context' in kwargs:
            self.context = kwargs.get("context")

        super().__init__(PostMention, BoardMention, OPMention)

    def render_post_mention(self, token):
        _output = ""

        target_post = get_post(token.target_post_id)

        if not target_post:
            _output = f"++{token.target_post_id}"
            return _output

        if target_post.is_removed:
            _output += "<del>"

        if self.context and (self.context.has_comment(target_post.id) or target_post.id == self.context.id):
            _output += f'<a href="{self.context.permalink}#p{target_post.id}">++{target_post.id}'

            if target_post.id == self.context.id:
                _output += " (OP)"

            _output += "</a>"
        else:
            _output += f'<a href="{target_post.permalink}">+++{target_post.board.name}/{target_post.id}</a>'

        if target_post.is_removed:
            _output += "</del>"

        return _output

    def render_board_mention(self, token):
        print("render board mention...")

        _output = ""

        target_board = get_board(token.target_board_name)

        if not target_board:
            _output = f"+++{token.target_board_name}"
            return _output

        if target_board.is_banned:
            _output += "<del>"

        _output += f'<a href="{target_board.url}">+++{target_board.name}</a>'

        if target_board.is_banned:
            _output += "</del>"

        return _output

    def render_op_mention(self, token):
        if not self.context:
            return "++OP"

        _output = f'<a href="{self.context.permalink}#p{self.context.id}">++{self.context.id} (OP)</a>'
        return _output

# add ref="nofollow noopener noreferrer" to outgoing links
def nofollow_noopener_noreferrer(attrs, new = False) -> str:
    attrs[(None, 'rel')] = "nofollow noopener noreferrer"

    return attrs

cleaner = Cleaner(tags = ALLOWED_TAGS,
    attributes = ALLOWED_ATTRS,
    protocols = ALLOWED_PROTOCOLS,
    filters = [partial(LinkifyFilter, callbacks = [nofollow_noopener_noreferrer], skip_tags = ['pre'])]
)

def render_md(text, context = None) -> str:
    _rendered = ""

    with CustomRenderer(context = context) as renderer:
        _rendered = renderer.render(Document(text))

    _rendered = cleaner.clean(_rendered)

    return _rendered
