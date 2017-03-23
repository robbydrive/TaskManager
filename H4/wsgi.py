from wsgiref.simple_server import make_server
import yaml
from example import Task


class WSGIApplication:

    def __init__(self, environment, start_response):
        print('Get request')
        self.environment = environment
        self.start_response = start_response
        self.headers = [
            ('Content-type', 'text/plain; charset=utf-8')
        ]

    @property
    def critical_tasks(self):
        with open("dataset.yml", 'r', encoding='utf-8') as stream:
            lll = yaml.load(stream)
            dataset = lll.get('dataset')
            if not isinstance(dataset, list):
                raise ValueError('wrong format')
            temp = []
            for i in range(len(dataset)):
                obj = Task(dataset[i][0], str(dataset[i][2]), dataset[i][1])
                delt = str(obj.remaining).split()[0]
                if int(delt) < 3 and dataset[i][1] == 'in_progress' or obj.is_failed is True:
                    temp += [dataset[i]]
        yield from temp


   ''' def __iter__(self):
        print('Wait for response')
        if self.environment.get('PATH_INFO', '/') == '/':
            yield from self.ok_response('Hello, World!')
        else:
            self.not_found_response()
        print('Done')

    def not_found_response(self):
        print('Create response')
        print('Send headers')
        self.start_response('404 Not Found', self.headers)
        print('Headers is sent')

    def ok_response(self, message):
        print('Create response')
        print('Send headers')
        self.start_response('200 OK', self.headers)
        print('Headers is sent')
        print('Send body')
        return self.critical_tasks()
       # yield ('%s\n' % message).encode('utf-8')
        print('Body is sent')
'''

if __name__ == '__main__':
    server = make_server('127.0.0.1', 9090, WSGIApplication)
    server.serve_forever()