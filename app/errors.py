"""Errors that can be returned safely by the HTTP API."""


class BotError(Exception):
    status_code = 502
    code = "provider_error"
    message = "The language-model provider could not complete the request."


class ConfigurationError(BotError):
    status_code = 503
    code = "configuration_error"
    message = "The bot is missing its provider configuration."


class RateLimitError(BotError):
    status_code = 429
    code = "rate_limited"
    message = "The language-model provider is rate limiting requests."

