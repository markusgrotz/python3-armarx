import logging
import threading

from armarx import TextListenerInterfacePrx

from armarx import TextToSpeechStateInterface
from armarx import TextToSpeechStateType

from armarx_core import ice_manager

logger = logging.getLogger(__name__)


class TextStateListener(TextToSpeechStateInterface):
    """
    A simple text state listener class.
    """

    def __init__(self):
        super().__init__()
        self.cv = threading.Condition()
        self.state = TextToSpeechStateType.eIdle
        self.tts = ice_manager.get_topic(TextListenerInterfacePrx, "TextToSpeech")

    def reportState(self, state, c=None):
        with self.cv:
            self.state = state
            self.cv.notify()

    def on_connect(self):
        """ """
        logger.debug("Registering TextListener")
        self._proxy = ice_manager.register_object(self, self.__class__.__name__)
        ice_manager.using_topic(self._proxy, self.__class__.__name__ + ".Listener")

    def is_idle(self) -> bool:
        """
        Returns true if the TTS system is idle
        """
        return self.state == TextToSpeechStateType.eIdle

    def say(self, text: str) -> None:
        """
        verbalize text.  The methods waits until the TTS system is idle.
        The text can be either a plain string or SSML markup.
        ..see:: https://cloud.google.com/text-to-speech/docs/ssml


        :param text: the text to report to the TTS system
        """
        self.cv.wait_for(lambda: self.is_idle(), timeout=30)
        self.tts.reportText(text)
