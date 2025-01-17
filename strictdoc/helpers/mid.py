import uuid


class MID:
    def __init__(self, mid: str):
        assert isinstance(mid, str), mid
        self.mid: str = mid

    @staticmethod
    def create() -> "MID":
        return MID(uuid.uuid4().hex)

    def __str__(self):  # pylint: disable=invalid-str-returned
        assert 0, "Must not be used"

    def __repr__(self):  # pylint: disable=invalid-repr-returned
        assert 0, "Must not be used"

    def __hash__(self):
        return self.mid.__hash__()

    def __eq__(self, other):
        assert isinstance(other, MID), other
        return self.mid == other.mid

    def get_string_value(self):
        return self.mid
