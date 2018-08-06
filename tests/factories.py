import factory
from demo.sample.models import Author, Book
from django.contrib.auth import get_user_model
from factory import fuzzy

from unicef_attachments import models


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")

    class Meta:
        model = get_user_model()


class AttachmentFileTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FileType
        django_get_or_create = ('code', )

    code = fuzzy.FuzzyText()
    name = factory.Sequence(lambda n: 'file_type_%d' % n)


class AttachmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Attachment


class AttachmentLinkFactory(factory.django.DjangoModelFactory):
    attachment = factory.SubFactory(AttachmentFactory)

    class Meta:
        model = models.AttachmentLink


class AuthorFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = Author


class BookFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    author = factory.SubFactory(AuthorFactory)

    class Meta:
        model = Book
