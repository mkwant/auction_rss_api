from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from routers.rss import router

# TODO Add function to generate random User Agent
# TODO Move code to src subdir
# TODO Translate as dependency Class: https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/

app = FastAPI(
    title='Auction to RSS',
    version='1.5.0'
)


@app.middleware("http")
async def add_noindex(request: Request, call_next):
    """Adding x-robots-tag to response headers to exclude from search engines."""
    response = await call_next(request)
    response.headers["x-robots-tag"] = 'noindex, nofollow'
    return response


@app.get(path='/', include_in_schema=False)
def docs_redirect():
    return RedirectResponse(url='/docs')


app.include_router(router)
