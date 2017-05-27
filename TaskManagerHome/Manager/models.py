from datetime import date, timedelta, datetime
from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.db.models import Min, Max, Sum, F
from django.db.models.functions import Trunc
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(max_length=200, unique=True, verbose_name="Email")
    phone = models.CharField(max_length=50, verbose_name="Phone number")
    first_name = models.CharField(max_length=50, verbose_name="First name")
    last_name = models.CharField(max_length=50, verbose_name="Last name")
    age = models.PositiveIntegerField(blank=True, verbose_name="Age", null=True)
    region = models.CharField(max_length=100, blank=True, verbose_name="Region", null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'first_name', 'last_name']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return f'{self.first_name}'


class Roadmap(models.Model):
    title = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="roadmaps")

    def __str__(self):
        return self.title

    @property
    def today(self):
        return self.tasks.filter(estimate=date.today(), roadmap=self)

    @property
    def min_date(self):
        created_date = Task.objects.filter(roadmap=self).aggregate(min_date=Min('created'))
        created_date = created_date if created_date is not None else date(year=2017, month=1, day=2)
        return created_date['min_date']

    @property
    def max_date(self):
        created_date = Task.objects.filter(roadmap=self).aggregate(max_date=Max('created'))
        finished_date = Task.objects.filter(roadmap=self).aggregate(max_date=Max('finished'))
        created_date['max_date'] = created_date['max_date'] if created_date['max_date'] is not None \
            else date(year=2017, month=1, day=1)
        finished_date['max_date'] = finished_date['max_date'] if finished_date['max_date'] is not None \
            else date(year=2017, month=1, day=1)
        return max(created_date['max_date'], finished_date['max_date'])

    @staticmethod
    def created_and_finished_stat(roadmap_id, user):
        roadmap = Roadmap.objects.filter(user=user).get(pk=roadmap_id)
        min_date = roadmap.min_date
        min_date = datetime.strptime(f'{min_date.year}-{min_date.isocalendar()[1]}-1', '%Y-%W-%w').date()
        max_date = roadmap.max_date
        created_and_finished = []
        current = min_date
        queryset = Task.objects.filter(roadmap=roadmap_id, user=user)
        while current <= max_date:
            created_and_finished.append({
                'year': current.year,
                'weekno': current.isocalendar()[1],
                'start_date': current.strftime("%Y-%m-%d"),
                'end_date': (current + timedelta(days=6)).strftime("%Y-%m-%d"),
                'created_count': queryset.filter(created__range=[current, current + timedelta(days=6)]) \
                                         .count(),
                'finished_count': queryset.filter(state=Task.READY,
                                                  finished__range=[current, current + timedelta(days=6)]) \
                                          .count()
            })
            current += timedelta(weeks=1)
            print(current)
        return created_and_finished

    @staticmethod
    def points_stat(roadmap_id, user):
        months_stat = Scores.objects.filter(task__user=user, task__roadmap=roadmap_id) \
                               .annotate(year_month=Trunc('date', 'month')) \
                               .order_by('year_month') \
                               .values('year_month') \
                               .annotate(points=Sum('points'))
        return months_stat

    class Meta:
        db_table = 'roadmaps'


class Task(models.Model):

    IN_PROGRESS = 'in_progress'
    READY = 'ready'
    CHOICES = (
        (IN_PROGRESS, 'In progress',),
        (READY, 'Ready',)
    )

    title = models.CharField(max_length=30)
    estimate = models.DateField()
    state = models.CharField(max_length=11, choices=CHOICES, default=IN_PROGRESS, blank=False)
    roadmap = models.ForeignKey(Roadmap,
                                on_delete=models.CASCADE,
                                blank=True,
                                null=True,
                                related_name='tasks'
                               )
    created = models.DateField(auto_now_add=True)
    finished = models.DateField(null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tasks")

    def ready(self):
        if Task.objects.get(pk=self.pk).state != Task.READY:
            self.state = Task.READY
            self.finished = date.today()
            try:
                with transaction.atomic():
                    self.save()
                    Scores.objects.create(points=self.points_to_accrue, task=self)
                    return True
            except IntegrityError as e:
                print(e) # TO DO: set up logging
        self.save()
        return False

    @property
    def points_to_accrue(self):
        """
        Formula: (estimate - today + 1) / (estimate - created) * (tasks completed in time in %)
        if task is failed, then division part equals minimum positive number (according to formula)
        code to assign points to user for task

        :return: possible amount of points to add to roadmap account as for today
        """
        finished = Task.objects.filter(roadmap=self.roadmap, state=Task.READY).count() \
                  if Task.objects.filter(roadmap=self.roadmap, state=Task.READY).count() > 0 \
                  else 1
        percent = Task.objects.filter(roadmap=self.roadmap, finished__lte=F('estimate')).count() \
                  / finished * 100.0
        return (self.estimate - date.today() + timedelta(days=1)) / (self.estimate - self.created) * percent

    @property
    def remaining(self):
        if self.state == Task.IN_PROGRESS and not self.is_failed:
            return self.estimate - date.today()
        return timedelta()

    @property
    def is_critical(self):
        return self.state == Task.IN_PROGRESS and self.remaining.days <= 3 and self.estimate >= date.today()

    @property
    def is_failed(self):
        return self.state == Task.IN_PROGRESS and self.estimate < date.today()

    class Meta:
        db_table = 'tasks'
        ordering = ('state', 'estimate')


class Scores(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    points = models.DecimalField(max_digits=10, decimal_places=2)
    task = models.ForeignKey(Task, on_delete=models.DO_NOTHING, related_name='points')

    class Meta:
        db_table = 'scores'
