class BaseException(Exception):
    def __init__(self, for_user, for_admin, extra_details=None):
        self.for_user = for_user
        self.for_admin = for_admin
        self.extra_details = extra_details

    def __str__(self):
        return (
            f"{self.__class__.__name__}(\n\tfor_user='{self.for_user}',\n\t"
            f"for_admin='{self.for_admin}',\n\textra_details='{self.extra_details}')"
        )

    def __repr__(self):
        return(
            f"{self.__class__.__name__}(\n\tfor_user='{self.for_user}',\n\t"
            f"for_admin='{self.for_admin}',\n\textra_details='{self.extra_details}')"
        )
