class APIError(Exception):
    def __init__(self, status: int, error_type: str, title: str, detail: str):
        self.status = status
        self.error_type = error_type
        self.title = title
        self.detail = detail
