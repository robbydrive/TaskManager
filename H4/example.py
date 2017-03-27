from datetime import datetime


class Task:
    def __init__(self, title, estimate):
        self.title = title
        self.estimate = estimate
        self.state = 'in_progress'

    @property
    def remaining(self):
        if self.state == 'in_progress':
            return datetime.date(datetime.strptime(self.estimate, '%Y-%m-%d')) \
                   - datetime.date(datetime.now())
        else:
            return 0

    @property
    def is_failed(self):
        delta = str(datetime.date(datetime.now()) - datetime.date(datetime.strptime(self.estimate, '%Y-%m-%d')))
        if delta.find('day') == -1:
            delta = '0'
        else:
            delta = delta.split()[0]
        return self.state == 'in_progress' and int(delta) > 0

    def ready(self):
        self.state = 'ready'

    def __str__(self):
        return f'{self.title} {self.state} {self.estimate} Is failed: {self.is_failed}'


class Roadmap:
    def __init__(self, tasks=[]):
        self.tasks = tasks

    def add_tasks(self, new_task):
        self.tasks.append(new_task)

    @property
    def today(self):
        current = []
        for element in self.tasks:
            if datetime.date(datetime.strptime(element.estimate, '%Y-%m-%d')) == datetime.date(datetime.now()):
                current.append(element)
        return current

    def filter(self, state):
        filtered_result = []
        for element in self.tasks:
            if element.state == state:
                filtered_result.append(element)
        return filtered_result

if __name__ == '__main__':
    roadmap = Roadmap()
    for i in range(3):
        task = Task('task %s' % i, '2017-3-27')
        roadmap.add_tasks(task)
    for k in roadmap.today:
        print(k)
