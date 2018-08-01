from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Book(models.Model):
    author = models.ForeignKey(
        Author,
        related_name="books",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name
