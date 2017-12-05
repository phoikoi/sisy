"""
CLI command to send tick messages for sisy
"""
from django.core.management.base import BaseCommand
from channels import Channel
import time
from sisy import HEARTBEAT_CHANNEL, HEARTBEAT_FREQUENCY

class Command(BaseCommand):
    """Management command which runs an infinite loop,
    sending messages to the clock channel (``sisy.CLOCK_CHANNEL``)
    in order to provide the basis for sisy's repeating
    tasks.
    """
    def handle(self, *args, **options):
        """Handle CLI command"""
        try:
            while True:
                Channel(HEARTBEAT_CHANNEL).send({'time':time.time()})
                time.sleep(HEARTBEAT_FREQUENCY)
        except KeyboardInterrupt:
            print("Received keyboard interrupt, exiting...")
