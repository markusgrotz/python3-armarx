from armarx import TextListenerInterfacePrx

from armarx import TextToSpeechStateInterface
from armarx import TextToSpeechStateType

import sys
import logging
import threading

logger = logging.getLogger(__name__)

from armarx import ice_manager


class TextStateListener(TextToSpeechStateInterface):

    def __init__(self):
        super(TextToSpeechStateInterface, self).__init__()
        self.cv = threading.Condition()
        self.state = TextToSpeechStateType.eIdle
        self.tts = TextListenerInterfacePrx.get_topic()

    def reportState(state, c=None):
        with self.cv:
            self.state = state
            if self.is_idle():
               self.cv.notify()

    def register(self):
        logger.debug('Registering TextListener')
        self._proxy = ice_manager.register_object(self, self.__class__.__name__)
        ice_manager.using_topic(self._proxy, self.__class__.__name__ + '.Listener')


    def is_idle(self):
        return self.state == TextToSpeechStateType.eIdle

    def say(self, text):
        self.cv.wait_for(lambda: self.is_idle(), timeout=30)
        self.tts.reportText(text)

from armarx import PlatformNavigatorInterfacePrx
from armarx import GazeControlInterfacePrx
from armarx import ElasticFusionInterfacePrx

from armarx.slice_loader import load_armarx_slice
load_armarx_slice('ArmarXCore', 'components/EmergencyStopInterface.ice')
from armarx.ice_manager import get_proxy


from armarx import EmergencyStopMasterInterfacePrx
from armarx import EmergencyStopState
from armarx.speech import TextStateListener


class Robot(object):

    def __init__(self):
        self._text_state_listener = TextStateListener()
        self._text_state_listener.register()


        self.platform = PlatformNavigatorInterfacePrx.get_proxy()
        self.gaze = GazeControlInterfacePrx.get_proxy()
        #self._fusion = ElasticFusionInterfacePrx.get_proxy()
        self.stop = get_proxy(EmergencyStopMasterInterfacePrx, 'EmergencyStopMaster')


    def say(self, text):
        self._text_state_listener.say(text)

    def scan_scene(self):
        pass

    def stop(self):
        self.stop.setEmergencyStopState(EmergencyStopState.eEmergencyStopActive)


from armarx import HandUnitInterfacePrx

class A6(Robot):

    def __init__(self):
        super().__init__()
        self.left_hand = HandUnitInterfacePrx.get_proxy('LeftHandUnit')
        self.right_hand = HandUnitInterfacePrx.get_proxy('RightHandUnit')

    def grasp(self, object_name):
        pass

    def open_hands(self):
        shape_name = 'Open'
        self.left_hand.setShape(shape_name)
        self.right_hand.setShape(shape_name)


