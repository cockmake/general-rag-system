class ResponseWrapper:
    def __init__(self, content: str | list):
        self.content = content

    def __repr__(self):
        return f"ResponseWrapper(content='{self.content}')"