from django.db import models
import django.contrib.postgres.fields as pgmodels

# Create your models here.
class Document(models.Model):
    num_pages = models.IntegerField()
    title = models.CharField(max_length=2000, default='unknown')
    slug = models.SlugField(blank=True, max_length=300)


class Page(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    text = models.TextField()
    

class Prediction(models.Model):
    text = models.TextField()
    score = models.IntegerField()

    def __str__(self):
        return self.text

class PrefixSuffixPrediction(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    type = models.CharField(max_length=200, default='unknown')
    predictions = models.ManyToManyField(Prediction)

    def __str__(self):
        return self.type + "prediction"
    


   # predictions = pgmodels.ArrayField(models.ForeignKey(Prediction, on_delete=models.CASCADE), size=10)

