import threading

import dataclasses as dc
import typing as ty

import armarx_skills.manager.dti

from armarx_core.time import date_time
from armarx_memory.aron import aron_dataclass
from armarx_memory.ice_conv.ice_converter import IceConverter
from armarx_skills.provider import dto

from armarx_skills.provider import skill_id
from armarx_skills.provider import skill_description
from armarx_skills.provider import skill_status_update

CallbackT = ty.Callable[[aron_dataclass.AronDict], None]


@dc.dataclass
class InitInput:
    executor_name: str
    params: aron_dataclass.AronDict


@dc.dataclass
class InitResult:
    status: skill_status_update.TerminatedSkillStatus

@dc.dataclass
class MainInput:
    executor_name: str
    params: aron_dataclass.AronDict
    callback: CallbackT


@dc.dataclass
class MainResult:
    status: skill_status_update.TerminatedSkillStatus
    data: aron_dataclass.AronDict = None


@dc.dataclass
class ExitInput:
    executor_name: str
    params: aron_dataclass.AronDict


@dc.dataclass
class ExitResult:
    status: skill_status_update.TerminatedSkillStatus


class Skill:
    CallbackT = CallbackT
    InitInput = InitInput
    InitResult = InitResult
    MainInput = MainInput
    MainResult = MainResult
    ExitInput = ExitInput
    ExitResult = ExitResult

    def __init__(
            self,
            description: skill_description.SkillDescription,
    ):
        # Public:
        self.description = description

        self.started_timestamp_usec = date_time.INVALID_TIME_USEC
        self.exited_timestamp_usec = date_time.INVALID_TIME_USEC

        self.manager: armarx_skills.manager.dti.SkillManagerInterfacePrx = None

        self.provider_name = "INVALID PROVIDER NAME"

        # Protected
        self._callbacks: ty.List[ty.Tuple[ty.Callable[[], bool], ty.Callable[[], None]]] = []
        self._callbacks_lock = threading.Lock()

        # Should not need atomic_bool-like type in Python.
        self._running: bool = False
        self._stopped: bool = False
        self._timeout_reached: bool = False

        # Private:
        self._condition_checking_thread: ty.Optional[threading.Thread] = None
        self.condition_checking_thread_frequency_hz: float = 20.0

    # Public:

    def get_skill_id(self) -> skill_id.SkillID:
        return skill_id.SkillID(
            provider_name=self.provider_name,
            skill_name=self.description.skill_name,
        )

    def is_skill_available(self, inp: InitInput) -> bool:
        return self.is_available(inp)

    def reset_skill(self):
        self.started_timestamp_usec = date_time.INVALID_TIME_USEC
        self.exited_timestamp_usec = date_time.INVALID_TIME_USEC

        self._running = False
        self._stopped = False
        self._timeout_reached = False

        self.reset()

    def wait_for_dependencies_of_skill(self):
        return self.wait_for_dependencies()

    def init_skill(self, inp: InitInput) -> InitResult:
        pass

    def main_of_skill(self, inp: MainInput) -> MainResult:
        pass

    def exit_skill(self, inp: ExitInput) -> ExitResult:
        pass

    def notify_skill_to_stop_asap(self):
        pass

    def check_whether_skill_should_stop_asap(self) -> bool:
        pass

    def is_stop_requested(self) -> bool:
        return self.check_whether_skill_should_stop_asap()

    def execute_full_skill(self, inp: MainInput) -> MainResult:
        pass

    # Protected:

    @classmethod
    def _make_aborted_result(cls) -> MainResult:
        pass

    def _notify_timeout_reached(self):
        pass

    def _init(self):
        self._callbacks.clear()
        self._running = True
        self.started_timestamp_usec = date_time.time_usec()

        def condition():
            return date_time.time_usec() >= (self.started_timestamp_usec + self.description.timeout_usec)

        self._install_condition_with_callback(condition, self._notify_timeout_reached)

        def thread_fn():
            pass

        self._condition_checking_thread = threading.Thread()
        self._condition_checking_thread.start()

    def _main(self):
        pass

    def _exit(self):
        pass

    def _install_condition_with_callback(
            self,
            condition: ty.Callable[[], bool],
            callback: ty.Callable[[], None],
    ):
        with self._callbacks_lock:
            self._callbacks.append((condition, callback))

    # Private:

    def is_available(self, init: InitInput) -> bool:
        return True

    def reset(self):
        pass

    def wait_for_dependencies(self):
        pass

    def init(self, inp: InitInput) -> InitResult:
        pass

    def main(self, inp: MainInput) -> MainResult:
        pass

    def exit(self, inp: ExitInput) -> ExitResult:
        pass

    def on_timeout_reached(self):
        pass

    def on_stop_requested(self):
        pass
