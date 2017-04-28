from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=30)
    estimate = models.DateField()
    state = models.CharField(max_length=11)
    roadmap = models.ForeignKey(Roadmap,
                                on_delete=models.SET_NULL(),
                                blank=True,
                                null=True,
                                )

    class Meta:
        db_table = 'tasks'


class Roadmap(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        db_table = 'roadmaps'
