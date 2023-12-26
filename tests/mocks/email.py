from email.message import EmailMessage


class MockEmail:
    _verify_codes: dict[str, int] = dict()

    def __init__(self, sender: EmailMessage):
        self.msg = sender

    def send(self, to_email: str, verify_code: int) -> None:
        self._verify_codes[to_email] = verify_code

    @classmethod
    def get_verify_code(cls, email: str) -> int:
        return cls._verify_codes[email]


def get_mock_email_sender() -> MockEmail:
    return MockEmail(EmailMessage())
