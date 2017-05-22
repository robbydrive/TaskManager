from datetime import date, timedelta
from django.db import models
from django.db.models import F
from django.utils.timezone import now

IN_PROGRESS = 'in_progress'
READY = 'ready'
CHOICES = (
    (IN_PROGRESS, 'In progress',),
    (READY, 'Ready',)
)


class Roadmap(models.Model):
    title = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def today(self):
        return Task.objects.filter(estimate=date.today())

    class Meta:
        db_table = 'roadmaps'


class Task(models.Model):
    title = models.CharField(max_length=30)
    estimate = models.DateField()
    state = models.CharField(max_length=11, choices=CHOICES, default=IN_PROGRESS, blank=False)
    roadmap = models.ForeignKey(Roadmap,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True,
                               )
    created = models.DateField(auto_now_add=True)
    finished = models.DateField(null=True)

    def ready(self):
        if self.state != READY:
            self.state = READY
            self.finished = date.today()
            self.save()
            # Formula: (estimate - today + 1) / (estimate - created) * (tasks completed in time in % from all tasks)
            # if task is failed, then division part equals minimum positive number (according to formula)
            # code to assign points to user for task
            percent = Task.objects.filter(finished__lte=F('estimate')).count() \
                      / Task.objects.filter(state=READY) * 100.0
            Scores.objects.create(points=(self.estimate-date.today()+1) / (self.estimate-self.created) * percent,
                                  task=self)
            return True
        return False

    @property
    def remaining(self):
        if self.state == IN_PROGRESS and not self.is_failed:
            return self.estimate - date.today()
        return timedelta()

    @property
    def is_critical(self):
        return self.state == IN_PROGRESS and self.remaining.days <= 3 and self.estimate >= date.today()

    @property
    def is_failed(self):
        return self.state == IN_PROGRESS and self.estimate < date.today()

    class Meta:
        db_table = 'tasks'
        ordering = ('state', 'estimate')


class Scores(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    points = models.DecimalField(max_digits=4, decimal_places=2)
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'scores'
