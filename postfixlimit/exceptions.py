class LimitException(Exception):
    pass

class LimitExceeded(LimitException):
    def __init__(self, action: str = "DEFER", message: str = "Limit exceeded"):
        self.action = action
        self.message = message
        super().__init__(f"{action} {message}")
    
    def postfix_response(self) -> str:
        return f"{self.action} {self.message}"
