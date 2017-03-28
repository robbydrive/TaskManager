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
        tasks = []
        with open("dataset.yml", 'r', encoding='utf-8') as stream:
            lll = yaml.load(stream)
            dataset = lll.get('dataset')
            if not isinstance(dataset, list):
                raise ValueError('wrong format')
            for i in range(len(dataset)):
                obj = Task(dataset[i][0], str(dataset[i][2]))
                obj.state = dataset[i][1]
                if obj.remaining < 3 and dataset[i][1] == 'in_progress' or obj.is_failed is True:
                    tasks.append(obj)
        return tasks

    def __iter__(self):
        print('Wait for response')
        if self.environment.get('PATH_INFO', '/') == '/':
            self.ok_response()
            yield '\n'.join([str(task) for task in self.critical_tasks]).encode()
        else:
            self.not_found_response()
            yield b''
        print('Done')

    def not_found_response(self):
        print('Create response')
        print('Send headers')
        self.start_response('404 Not Found', self.headers)
        print('Headers is sent')

    def ok_response(self):
        print('Create response')
        print('Send headers')
        self.start_response('200 OK', self.headers)
        print('Headers is sent')
        print('Send body')


if __name__ == '__main__':
    server = make_server('127.0.0.1', 9090, WSGIApplication)
    server.serve_forever()
