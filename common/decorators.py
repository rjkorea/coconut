# -*- coding: utf-8 -*-

import functools

from tornado.web import HTTPError

import settings


def admin_auth_async(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        self.current_user = await self.get_current_admin_async()
        if not self.current_user:
            raise HTTPError(401, 'Permission denied')
        else:
            result = method(self, *args, **kwargs)
            if result:
                await result
    return wrapper


def user_auth_async(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        self.current_user = await self.get_current_user_async()
        if not self.current_user:
            raise HTTPError(401, 'Permission denied')
        else:
            result = method(self, *args, **kwargs)
            if result:
                await result
    return wrapper


def app_auth_async(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        config = settings.settings()
        mobile_app_key = await self.get_current_app_async()
        if mobile_app_key != config['application']['mobile']['ipad_id']:
            raise HTTPError(401, 'Permission denied')
        else:
            result = method(self, *args, **kwargs)
            if result:
                await result
    return wrapper


def tablet_auth_async(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        self.current_user = await self.get_current_tablet_async()
        if not self.current_user:
            raise HTTPError(401, 'Permission denied')
        else:
            result = method(self, *args, **kwargs)
            if result:
                await result
    return wrapper


def parse_argument(key_type_defaults):
    def decorator(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            parsed_args = dict()
            try:
                for k, t, d in key_type_defaults:
                    if t == list:
                        parsed_args[k] = self.get_arguments(k)
                    else:
                        val = self.get_argument(k, None)
                        try:
                            parsed_args[k] = t(val) if val is not None else d
                        except Exception as e:
                            parsed_args[k] = d
                kwargs['parsed_args'] = parsed_args
                result = method(self, *args, **kwargs)
                if result:
                    await result
            except ValueError as e:
                raise HTTPError(400, str(e))

        return wrapper

    return decorator
