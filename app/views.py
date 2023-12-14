from typing import Optional

from aiohttp import web
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import check_owner, check_password, check_token, hash_password
from crud import select_one, create_item, delete_item, get_item_by_id, update_item
from errors import Unauthorized
from models import Advt, Token, User
from schema import SCHEMA_MODEL, CreateAdvt, CreateUser, Login, PatchUser
from tools import validate


class BaseView(web.View):
    @property
    def session(self) -> AsyncSession:
        return self.request.session

    @property
    def token(self) -> Token:
        return self.request.token

    @property
    def user(self) -> User:
        return self.request.token.user

    async def validated_json(self, schema: SCHEMA_MODEL):
        raw_json = await self.request.json()
        return validate(schema, raw_json)


class UserView(BaseView):
    @check_token
    async def get(self):
        return web.json_response(self.user.dict)

    async def post(self):
        payload = await self.validated_json(CreateUser)
        payload["password"] = hash_password(payload["password"])
        user = await create_item(User, payload, self.session)
        return web.json_response({"id": user.id})

    @check_token
    async def patch(self):
        payload = await self.validated_json(PatchUser)
        user = await update_item(self.token.user, payload, self.session)
        return web.json_response({"id": user.id})

    @check_token
    async def delete(self):
        await delete_item(self.token.user, self.session)
        return web.json_response({"status": "ok"})


class LoginView(BaseView):
    async def post(self):
        payload = await self.validated_json(Login)
        query = select(User).where(User.name == payload["name"]).limit(1)
        user = await select_one(query, self.session)
        if user is None:
            raise Unauthorized("invalid user or password")
        if check_password(payload["password"], user.password):
            token = await create_item(Token, {"user_id": user.id}, self.session)
            # add_item(token, self.session)
            return web.json_response({"token": str(token.token)})
        raise Unauthorized("invalid user or password")


class AdvtView(BaseView):

    @property
    def advt_id(self) -> Optional[int]:
        advt_id = self.request.match_info.get("advt_id")
        return int(advt_id) if advt_id else None

    @check_token
    async def get(self, advt_id: int = None):
        if advt_id is None:
            return web.json_response([advt.dict for advt in self.user.advts])
        advt = await get_item_by_id(Advt, advt_id, self.session)
        check_owner(advt, self.token.user_id)
        return web.json_response(advt.dict)

    @check_token
    async def post(self):
        payload = await self.validated_json(CreateAdvt)
        payload['user_id'] = self.token.user_id
        advt = await create_item(Advt, payload, self.session)
        # advt = create_item(
        #     Advt, dict(owner_id=self.token.user_id, **payload), self.session
        # )
        return web.json_response({"id": advt.id})

    @check_token
    async def delete(self):
        advt = await get_item_by_id(Advt, self.advt_id, self.session)
        check_owner(advt, self.token.user_id)
        await delete_item(advt, self.session)
        return web.json_response({"status": "ok"})
