from sqlmodel import Session


class Repository:
    def __init__(self, session: Session) -> None:
        self.session = session
