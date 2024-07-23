"""Dummy Device."""


class Md:
    """Dummy Device."""

    def __init__(self) -> None:
        """Initialize."""
        self._host = "dyson.rexkramer.de"
        self._value = 0

    @property
    def device(self):
        """Return device."""
        return self._host

    def result(self):
        """Retrieve value."""
        while True:
            self._value += 1
            yield self._value


if __name__ == "__main__":
    m = Md()
    print(next(m.result()))
    print(next(m.result()))
    print(next(m.result()))
