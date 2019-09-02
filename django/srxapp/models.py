from django.db import models


class Cache(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    workingdict_origin = models.TextField(default="")
    srcfile_commithash = models.TextField(default="")

    def __str__(self):
        return self.name
