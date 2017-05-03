from datetime import date, timedelta
from django.db import models

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

    def ready(self):
        if self.state != READY:
            self.state = READY
            self.save()
            return True
        return False

    @property
    def remaining(self):
        if self.state == IN_PROGRESS and not self.is_failed:
            return self.estimate - date.today()
        else:
            return timedelta()

    @property
    def is_critical(self):
        return self.state == IN_PROGRESS and self.remaining.days <= 3

    @property
    def is_failed(self):
        return self.state == IN_PROGRESS and self.estimate < date.today()

    class Meta:
        db_table = 'tasks'
        ordering = ('state', 'estimate')
