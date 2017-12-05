from django.db import models

class BaseFoo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ModelFoo(BaseFoo):
    name = models.CharField(max_length=64)

    def InstanceMethod(self, message):
        task = message['task']
        print(f"Instance method of ModelFoo {self.pk} ({self.name}) running from task #{task.pk} ({task.label})")

    @classmethod
    def ClassMethod(cls, message):
        task = message['task']
        print(f"Class method of ModelFoo, running from task #{task.pk} ({task.label})")

    @staticmethod
    def StaticMethod(message):
        task = message['task']
        print(f"Static method of ModelFoo, running from task #{task.pk} ({task.label})")
