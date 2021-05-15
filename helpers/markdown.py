from mistletoe import Document, HTMLRenderer

def render(text):
    _rendered = ""

    with HTMLRenderer() as renderer:
        _rendered = renderer.render(Document(text))

    return _rendered
