from django.db import models

# Create your models here.
class Image(models.Model):
    name = models.CharField(max_length = 50, blank=True, null=True)
    url = models.URLField(blank=True, null=True) 
    picture = models.ImageField(upload_to='images/', blank=True, null=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    parent_picture = models.PositiveIntegerField(blank=True, null=True)

    def delete(self, using=None, keep_parents=False):
        self.picture.storage.delete(self.picture.name)
        super().delete()