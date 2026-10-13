# Define any custom exceptions to be used here


class NoCameraFoundError(Exception):
    """Raised when the camera connot be found"""

    def __init__(self, i: int) -> None:
        super().__init__(f"Camera at index {i} cannot be found.")
