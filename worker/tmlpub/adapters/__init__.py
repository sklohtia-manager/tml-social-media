"""Platform adapters. Each returns plain dicts; none prints or stores tokens."""


class Uncertain(Exception):
    """The remote may or may not have accepted the request. Never retry blindly: block for review."""


class AuthProblem(Exception):
    """Authentication or permission failure: alert immediately, do not retry."""
