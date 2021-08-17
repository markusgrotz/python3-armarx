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

    def reportState(self, state, c=None):
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

