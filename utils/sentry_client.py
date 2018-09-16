# coding: utf-8

from raven import Client
from raven.handlers.logging import SentryHandler


client = Client('https://78fd1a2e8324477382ffc2e8889cc304:bbbea6a6a4514798877a21df757f824c@sentry.hundun.cn/21')
handler = SentryHandler(client)
