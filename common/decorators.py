# -*- coding: utf-8 -*-

import functools

from tornado.web import HTTPError


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
