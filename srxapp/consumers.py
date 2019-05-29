import json
import time
import difflib
import logging

from channels.generic.websocket import WebsocketConsumer
from srxapp.utils import helpers

logger = logging.getLogger(__name__)


class SrxappWebsocketConsumer(WebsocketConsumer):

    def send(self, message):
        super().send(text_data=json.dumps({'message': message}))


class CheckConsumer(SrxappWebsocketConsumer):

    def receive(self, text_data):
        job_url = helpers.get_jenkins_job_url(commit='no')
        session = helpers.get_jenkins_session_object()

        # Activate Jenkins by calling the job url. Jenkins then will put it
        # into the building queue.
        job_request = session.post(job_url)
        if job_request.status_code != 201:
            error = 'Jenkins job request failed:\n{}'.format(job_request)
            self.send(error)
            logger(error)
            return
        queue_url = job_request.headers['Location']

        # Poll Jenkins until it provides a url for the build
        self.send('Starting Jenkins job')
        while True:
            queue_request = session.get('{}api/json/'.format(queue_url))
            queue_json = queue_request.json()
            if 'executable' in queue_json:
                self.send('\n')
                build_url = queue_json['executable']['url']
                break
            time.sleep(1)
            self.send('.')

        # Poll Jenkins for build output
        logger.info('Starting build at {}'.format(build_url))
        diff_data = ''
        while True:
            build_request = session.get('{}api/json/'.format(build_url))
            console_out = session.get('{}consoleText'.format(build_url))

            diff = difflib.context_diff(diff_data, console_out.text)
            delta = ''.join(l[2:] for l in diff if l.startswith('+ '))
            diff_data = ''.join([diff_data, delta])

            if delta != '':
                self.send(delta)

            build_json = build_request.json()
            if build_json['building'] is False:
                break
            time.sleep(1)


class DeploymentConsumer(SrxappWebsocketConsumer):

    def receive(self, text_data):
        pass
