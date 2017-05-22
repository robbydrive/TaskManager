from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.db import models, transaction
from django.db.models import Min, Max, Sum, F
from django.db.models.functions import Coalesce


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
        return Task.objects.filter(estimate=date.today(), roadmap=self)

    @property
    def min_date(self):
        created_date = Task.objects.filter(roadmap=self).aggregate(min_date=Min('created'))
        return created_date['min_date']

    @property
    def max_date(self):
        created_date = Task.objects.filter(roadmap=self).aggregate(max_date=Max('created'))
        finished_date = Task.objects.filter(roadmap=self).aggregate(max_date=Max('finished'))
        return max(created_date['max_date'], finished_date['max_date'])

    @staticmethod
    def created_and_finished_stat(roadmap_id):
        roadmap = Roadmap.objects.get(pk=roadmap_id)
        min_date = roadmap.min_date
        min_date = datetime.strptime(f'{min_date.year}-{min_date.isocalendar()[1]}-1', '%Y-%W-%w').date()
        max_date = roadmap.max_date
        created_and_finished = []
        current = min_date
        queryset = Task.objects.filter(roadmap=roadmap_id)
        while current <= max_date:
            created_and_finished.append({
                'year': current.year,
                'weekno': current.isocalendar()[1],
                'start_date': current.strftime("%Y-%m-%d"),
                'end_date': (current + timedelta(days=6)).strftime("%Y-%m-%d"),
                'created_count': queryset.filter(created__range=[current, current + timedelta(days=6)]) \
                                         .count(),
                'finished_count': queryset.filter(state=READY,
                                                  finished__range=[current, current + timedelta(days=6)]) \
                                          .count()
            })
            current += timedelta(weeks=1)
            print(current)
        return created_and_finished

    @staticmethod
    def points_stat(roadmap_id):
        roadmap = Roadmap.objects.get(pk=roadmap_id)
        min_date = roadmap.min_date
        min_date = datetime.strptime(f'{min_date.year}-{min_date.month}-01', '%Y-%m-%d').date()
        max_date = roadmap.max_date
        points = []
        current = min_date
        while current <= max_date:
            points.append({
                'month': current.strftime('%Y-%m'),
                'points': Scores.objects.filter(task__roadmap=roadmap,
                                                date__range=[current, current+relativedelta(months=1)-timedelta(days=1)])\
                                        .aggregate(total_points=Sum(Coalesce('points', 0.0))).get('points__sum', 0.0)
            })
            current += relativedelta(months=1)
        return points

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
            try:
                with transaction.atomic():
                    self.save()
                    # Formula: (estimate - today + 1) / (estimate - created) * (tasks completed in time in % from all tasks)
                    # if task is failed, then division part equals minimum positive number (according to formula)
                    # code to assign points to user for task
                    percent = Task.objects.filter(finished__lte=F('estimate')).count() \
                              / Task.objects.filter(state=READY) * 100.0
                    Scores.objects.create(points=(self.estimate-date.today()+1) / (self.estimate-self.created) * percent,
                                      task=self)
                    return True
            except Exception as e:
                print(e) # TO DO: set up logging
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
