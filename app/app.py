from aiohttp import web

from context import init_db
from middleware import http_errors_middleware, session_middleware
from views import LoginView, AdvtView, UserView
import logging


def _get_app() -> web.Application:
    app = web.Application()
    app.middlewares.extend([http_errors_middleware, session_middleware])
    app.cleanup_ctx.append(init_db)
    logging.basicConfig(level=logging.DEBUG)
    app.logger = logging.getLogger('app')
    app.add_routes(
        [
            web.post("/login", LoginView),
            web.get("/user", UserView),
            web.post("/user", UserView),
            web.patch("/user", UserView),
            web.delete("/user", UserView),
            web.post("/advertisement", AdvtView),
            web.get("/advertisement/{advt_id:\d+}", AdvtView),
            web.delete("/advertisement/{advt_id:\d+}", AdvtView),

        ]
    )

    return app


async def get_app():
    return _get_app()


if __name__ == "__main__":
    web.run_app(_get_app())
