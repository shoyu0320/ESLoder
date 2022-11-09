import string
import time
from typing import List, Optional, TypeVar, Union

_A = TypeVar("_A", bound="A2Z")


class A2Z:
    def __init__(self, full_set: str) -> None:
        self.count: int = 0
        self.alphabet: str = full_set
        self.max_size: int = len(self.alphabet)

    def increase(self) -> None:
        self.count += 1

    @property
    def position(self) -> int:
        return self.count % self.max_size

    @property
    def val(self) -> str:
        return self.alphabet[self.position]

    def __add__(self, other: _A) -> str:
        return self.val + other.val


class AbstractListMaker:
    progress_bar_style: str = "*/."
    bar_size: int = 20

    def __init__(self,
                 max_size: int = 100,
                 init: Optional[List[str]] = [],
                 assert_level: str = "none",
                 value_type: type = str
                ) -> None:
        assert max_size > 0, ("A value of max_size must be 1 or bigger.")
        self.max_size: int = max_size
        self.values: List[str] = self.init_list(init)
        self.assert_level: str = assert_level
        self.value_type: type = value_type
        self.previous: float = self.current
        self.init_time: float = self.previous

    def init_list(self, initial_values: Union[str, List[str]]) -> List[str]:
        if self.is_valid_for_list(initial_values):
            return list(initial_values)
        else:
            return [initial_values]

    def is_valid_for_list(self, val: Union[str, List[str]]) -> bool:
        valid: bool = True
        valid &= (isinstance(val, str) | isinstance(val, list))
        return valid

    @property
    def not_accomplished_icon(self) -> str:
        return self.progress_bar_style.split("/")[-1]

    @property
    def accomplished_icon(self) -> str:
        return self.progress_bar_style.split("/")[0]

    @property
    def float_progress(self) -> float:
        return self.list_size / self.max_size

    @property
    def percent_progress(self) -> float:
        return self.float_progress * 100

    @property
    def int_progress(self) -> int:
        return int(self.float_progress * self.bar_size)

    @property
    def not_accomplished_bar(self) -> str:
        not_accomplished: int = self.bar_size - self.int_progress
        return self.not_accomplished_icon * not_accomplished

    @property
    def accomplished_bar(self) -> str:
        return self.accomplished_icon * self.int_progress

    @property
    def current(self) -> float:
        return time.time()

    @property
    def elapsed_time(self) -> float:
        current: float = self.current
        elapsed: float = self.current - self.previous
        self.previous = current
        return elapsed

    @property
    def total_time(self) -> float:
        return self.current - self.init_time

    @property
    def remain_time(self) -> float:
        elapsed_total_time: float = self.total_time
        accomplished_rate: float = (self.float_progress + 1e-16)
        not_accomplished_rate: float = 1 - self.float_progress
        time_per_acc: float = elapsed_total_time / accomplished_rate
        remain_time: float = time_per_acc * not_accomplished_rate
        return remain_time

    def progress_bar(self) -> str:
        bar: str = self.accomplished_bar + self.not_accomplished_bar
        remain_sec: float = self.remain_time
        remain_day: int = int(remain_sec / 60 / 60 / 24)

        remain_sec = remain_sec - remain_day * 60 * 60 * 24
        remain_hr: int = int(remain_sec / 60 / 60)

        remain_sec = remain_sec - remain_hr * 60 * 60
        remain_min: int = int(remain_sec / 60)

        remain_sec = remain_sec - remain_min * 60
        remain_sec = int(remain_sec)

        text: str = (
            f"\r進捗度|{bar}:{self.percent_progress:.1f}%  "
            f"残時間|{remain_day:.0f}日{remain_hr:.0f}時間{remain_min:.0f}分{abs(remain_sec):.0f}秒     "
        )
        print(text, end="")

    def __contains__(self, val: str) -> bool:
        return val in self.values

    @property
    def list_size(self) -> int:
        return len(self.values)

    @property
    def done(self) -> bool:
        return len(self.values) == self.max_size

    def is_valid(self, val: str) -> bool:
        valid: bool = True
        valid &= isinstance(val, self.value_type)
        return valid

    def add(self, val: str) -> None:
        if self.is_valid(val):
            self.values.append(val)
        elif self.assert_level == "error":
            raise ValueError()

    def _method(self) -> str:
        raise NotImplementedError()

    def create(self):
        val: str
        count: int = 1
        while not self.done:
            val = self._method()
            self.add(val)
            count += 1
            self.progress_bar()


class A2ZListMaker(AbstractListMaker):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        a2z: str = string.ascii_uppercase
        self.first: A2Z = A2Z(a2z)
        self.second: A2Z = A2Z(a2z)

    def _method(self) -> str:
        val: str = self.first + self.second
        self.second.increase()

        if self.second.position == 0:
            self.first.increase()
        return val
