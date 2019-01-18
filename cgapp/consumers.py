from channels.generic.websocket import WebsocketConsumer
import json
import subprocess as sp


class ConsoleOut(WebsocketConsumer):

    def connect(self):
        self.accept()


    def disconnect(self, close_code):
        pass


    def receive(self, text_data):

        text_data_json = json.loads(text_data)
        cmdlist = text_data_json['message']


        cmd = ''
        for c in cmdlist:
            cmd = cmd + c + ' '
        cmd = cmd + '\n'

        self.send(text_data=json.dumps({
            'message': cmd
        }))


        p1 = sp.Popen(cmdlist, stdout=sp.PIPE)

        for line in p1.stdout:
            output = line.decode("utf-8")

            self.send(text_data=json.dumps({
                'message': output
            }))


        self.send(text_data=json.dumps({
            'message': '\n'
        }))