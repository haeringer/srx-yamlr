from channels.generic.websocket import WebsocketConsumer
import json
import subprocess as sp


class CheckConsumer(WebsocketConsumer):

    def receive(self, text_data):
        cmd = ['ping', '-c 5', '10.13.0.1']
        cmdstr = ''
        for c in cmd:
            cmdstr = cmdstr + c + ' '

        self.send(text_data=json.dumps({'message': cmdstr+'\n'}))

        proc = sp.Popen(cmd, stdout=sp.PIPE, universal_newlines=True)
        for output_line in proc.stdout:
            self.send(text_data=json.dumps({'message': output_line}))


class DeploymentConsumer(WebsocketConsumer):

    def receive(self, text_data):
        pass
