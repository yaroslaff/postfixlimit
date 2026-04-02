class LimitException(Exception):
    pass

class LimitExceeded(LimitException):
    def __init__(self, action: str = "DEFER", code: int = 452, message: str = "Limit exceeded"):
        self.action = action
        self.code = code
        self.message = message
        super().__init__(f"{action} {code} {message}")
    
    def postfix_response(self) -> str:
        return f"{self.action} {self.code} {self.message}"