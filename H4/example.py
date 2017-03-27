from datetime import datetime


class Task:
    def __init__(self, title, estimate):
        self.title = title
        self.estimate = datetime.date(datetime.strptime(estimate, "%Y-%m-%d"))
        self.state = 'in_progress'

    @property
    def remaining(self):
        if self.state == 'in_progress':
            return self.estimate - datetime.date(datetime.now())
        else:
            return 0

    @property
    def is_failed(self):
        delta = str(datetime.date(datetime.now()) - self.estimate)
        delta = '0' if delta.find('day') == -1 else delta.split()[0]
        return self.state == 'in_progress' and int(delta) > 0

    def ready(self):
        self.state = 'ready'

    def __str__(self):
        return f'{self.title} {self.state} {self.estimate} Is failed: {self.is_failed}'


class Roadmap:
    def __init__(self, tasks=[]):
        self.tasks = tasks

    def add_task(self, new_task):
        self.tasks.append(new_task)

    @property
    def today(self):
        return [task for task in self.tasks
                if task.estimate == datetime.date(datetime.now())]

    def filter(self, state):
        return [task for task in self.tasks
                if task.state == state]

if __name__ == '__main__':
    roadmap = Roadmap()
    for i in range(3):
        task = Task('task %s' % i, '2017-3-27')
        roadmap.add_task(task)
    for k in roadmap.tasks:
        print(k)
