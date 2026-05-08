from starlette.responses import Response


class XMLResponse(Response):
    """
    A subclass of starlette.responses.Response which will set the content
    to an RSS XML document.
    """
    media_type = 'application/xml'
    charset = 'utf-8'
