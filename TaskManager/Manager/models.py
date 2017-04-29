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

    class Meta:
        db_table = 'roadmaps'


class Task(models.Model):
    title = models.CharField(max_length=30)
    estimate = models.DateField()
    state = models.CharField(max_length=11, choices=CHOICES)
    roadmap = models.ForeignKey(Roadmap,
                                on_delete=models.SET_NULL,
                                blank=True,
                                null=True,
                               )

    class Meta:
        db_table = 'tasks'
