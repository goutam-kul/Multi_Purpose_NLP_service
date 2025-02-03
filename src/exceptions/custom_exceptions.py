class NLPServiceException(Exception):
    """Base Exception class for NLP service"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ModelConnectionError(NLPServiceException):
    """Raised when unable to connect to the model service"""
    def __init__(self, message: str = "Failed to connect to the model instance"):
        super().__init__(message, "MODEL_CONNECTION ERROR")

class InvalidModelResponseError(NLPServiceException):
    """Raise when model response is invalid or cannot be parsed"""
    def __init__(self, message: str = "Invalid model response"):
        super().__init__(message, "INVALID_MODEL_RESPONSE")

class ValidationError(NLPServiceException):
    """Raised when input validation fails"""
    def __init__(self, message: str = "Input validation failed"):
        super().__init__(message, "VALIDATION_ERROR")

class JSONParsingError(NLPServiceException):
    """Raise when JSON parsing fails"""
    def __init__(self, message: str = "Failed to parse JSON"):
        super().__init__(message, "JSON_PARSE_ERROR")

