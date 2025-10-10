import os


def get_sec_user_agent() -> str:
    env_agent = os.getenv("SEC_USER_AGENT")
    if env_agent:
        return env_agent
    return "SmartMoneyResearch/1.0 (contact: research@example.com)"


SEC_HEADERS = {
    "User-Agent": get_sec_user_agent(),
    "Accept": "application/json",
}

REQUEST_TIMEOUT = 20
YF_HISTORY_PERIOD_DEFAULT = "2y"
