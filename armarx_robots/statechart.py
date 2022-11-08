"""
A module with statechart related code
"""
import logging

from typing import Dict
from typing import Any

from armarx import SimpleStatechartExecutorInterfacePrx

from armarx import StateParameterIceBase

from armarx import SingleVariantBase
from armarx import VariantBase
from armarx import ContainerType

from armarx_core.variants import hash_type_name


class StatechartExecutor(object):
    """
    A convenience class to run statecharts using the SimpleStatechartExecutor
    component
    """

    def __init__(self, profile_name: str, group_name: str, state_name: str):
        self.fullname = f"{profile_name}{group_name}"
        self.state_name = state_name
        self.executor = SimpleStatechartExecutorInterfacePrx.get_proxy()
        self.logger = logging.getLogger(self.__class__.__name__)

    #  -> Ice.Future:
    def run(
        self,
        state_parameters: Dict[str, Any] = None,
        stop_current_statechart: bool = False,
    ):
        """
        Runs the statechart via the SimpleStatechartExecutor component

        :param state_parameters: the statechart parameters
        :param stop_current_statechart:  stop an already running statechart
        :returns: a future of the execution status
        """
        self.logger.info("running state %s of group %s", self.state_name, self.fullname)

        state_parameters = state_parameters or {}
        self.logger.debug("with parameters %s", state_parameters)

        preload_libraries = [v.ice_staticId() for k, v in state_parameters.items()]
        self.logger.debug("preloading libraries %s", preload_libraries)
        self.executor.preloadLibrariesFromHumanNames(preload_libraries)

        state_parameters: Dict[str, StateParameterIceBase] = {
            k: self._convert_parameter(v) for k, v in state_parameters.items()
        }

        if not self.executor.hasExecutionFinished():
            self.logger.warning("another statechart is currently executed.")
            if stop_current_statechart:
                self.logger.debug("stopping running statechart")
                self.executor.stopImmediatly()
            else:
                self.logger.debug("waiting for running statechart")
                return self.executor.waitUntilStatechartExecutionIsFinishedAsync()
        remote_name = f"{self.fullname}RemoteStateOfferer"
        self.logger.debug(
            "running state %s of remote state %s", self.state_name, remote_name
        )
        if not self.executor.startStatechart(
            remote_name, self.state_name, state_parameters
        ):
            self.logger.warning(
                "unable to run state %s of state %s", self.state_name, remote_name
            )
        return self.executor.waitUntilStatechartExecutionIsFinishedAsync()

    def get_output_parameters(self):
        """
        Returns the output parameters of the statechart
        """
        self.logger.debug("getting statechart output parameters")
        return self.executor.getOutputParameters()

    def stop(self):
        """
        Stops the current running statechart
        """
        self.logger.debug("stopping statechart execution")
        self.executor.stopImmediatly()

    @staticmethod
    def _convert_parameter(v):
        type_container = ContainerType(None, v.ice_staticId())
        v = VariantBase(v, hash_type_name(v.ice_staticId()))
        v = SingleVariantBase(type_container, v)
        return StateParameterIceBase(value=v, set=True)

    def __str__(self):
        return f"{self.__class__.__name__}{self.fullname}"
