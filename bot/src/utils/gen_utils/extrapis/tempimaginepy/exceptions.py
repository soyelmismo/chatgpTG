class InvalidCFGError(Exception):
    """Exception raised when the cfg parameter is invalid."""
    def __init__(self, exception):
        self.exception = exception
        self.message = f"Invalid CFG, must be in range (0; 16): "
        super().__init__(self.message + str(self.exception))

class AssetsRetrievalError(Exception):
    """Exception raised when there is an error retrieving assets."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while retrieving assets: "
        super().__init__(self.message + str(self.exception))

class VariationsError(Exception):
    """Exception raised when there is an error making variations."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while making variations: "
        super().__init__(self.message + str(self.exception))

class ImageGenError(Exception):
    """Exception raised when there is an error making the request."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while making the request: "
        super().__init__(self.message + str(self.exception))

class UpscalingError(Exception):
    """Exception raised when there is an error building the multipart data."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while building the multipart data: "
        super().__init__(self.message + str(self.exception))

class MultiPartDataError(Exception):
    """Exception raised when there is an error making upscale request."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while making upscale request: "
        super().__init__(self.message + str(self.exception))

class TranslationError(Exception):
    """Exception raised when there is an error translating the prompt."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while translating the prompt: "
        super().__init__(self.message + str(self.exception))

class InterrogatorError(Exception):
    """Exception raised when there is an error generating a prompt."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while generating a prompt: "
        super().__init__(self.message + str(self.exception))

class InpaintingError(Exception):
    """Exception raised when there is an error performing an inpainting."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while performing an inpainting: "
        super().__init__(self.message + str(self.exception))

class RemixingError(Exception):
    """Exception raised when there is an error image remixing."""
    def __init__(self, exception):
        self.exception = exception
        self.message = "An error occurred while image remixing: "
        super().__init__(self.message + str(self.exception))
