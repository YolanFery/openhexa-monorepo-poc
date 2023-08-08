from google.cloud._helpers import _bytes_to_unicode


class MockBlob:
    def __init__(
        self,
        name,
        bucket,
        size=None,
        content_type=None,
    ):
        self.name = _bytes_to_unicode(name)
        self.size = size
        self._content_type = content_type
        self.bucket = bucket

    @property
    def content_type(self):
        return self._content_type

    @property
    def updated(self):
        return None

    def __repr__(self) -> str:
        return f"<MockBlob: {self.name}>"
