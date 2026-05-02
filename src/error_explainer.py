class ErrorExplainer:
    ERROR_EXPLANATIONS = {
        "InvalidAMIID.NotFound": (
            "यह AMI image आपके region में available नहीं है।"
        ),
        "UnauthorizedOperation": (
            "आपके पास इस operation को करने की permission नहीं है।"
        ),
        "InsufficientInstanceCapacity": (
            "AWS के पास इस समय इस instance type के लिए capacity नहीं है।"
        ),
        "InvalidInstanceID.NotFound": (
            "यह instance ID मौजूद नहीं है या already delete हो चुकी है।"
        ),
        "RequestExpired": (
            "Request expire हो गई है। अपना system clock check करें।"
        ),
    }

    def explain_error(self, error: str, language: str = "hi") -> str:
        """Return a human-readable explanation for an AWS error string.

        Falls back to returning the raw error when no match is found.
        """
        for key, explanation in self.ERROR_EXPLANATIONS.items():
            if key in error:
                return explanation
        return f"Error: {error}"
