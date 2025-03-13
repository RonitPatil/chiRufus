class URLNotAccessibleError(Exception):
    def __init__(self, url, attempts=3, message=None):
        self.url = url
        self.attempts = attempts
        self.message = message or f"URL not accessible after {attempts} attempts: {url}"
        super().__init__(self.message) 