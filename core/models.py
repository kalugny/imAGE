from django.db import models
import json


GENDERS = (
    (0, 'Male'),
    (1, 'Female')
)


class Person(models.Model):
    name = models.CharField(max_length=128, primary_key=True)
    birth_date = models.DateField()
    gender = models.IntegerField(choices=GENDERS)

    def __str__(self):
        return self.name


class Picture(models.Model):
    file_path = models.CharField(max_length=255, primary_key=True)

    def static_path(self):
        return self.file_path.replace(r'C:\Code\faces\FershtmanPics', 'Pics')

    def to_dict(self):
        return {
            'path': self.static_path(),
            'faces': [f.to_dict() for f in self.detectedface_set.all()]
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class DetectedFace(models.Model):
    face_id = models.CharField(max_length=64, primary_key=True)
    picture = models.ForeignKey('Picture')
    age = models.FloatField()
    gender = models.IntegerField(choices=GENDERS)
    rect_top = models.IntegerField()
    rect_left = models.IntegerField()
    rect_width = models.IntegerField()
    rect_height = models.IntegerField()
    person = models.ForeignKey('Person', null=True)

    def to_dict(self):
        return {
            'face_id': self.face_id,
            'picture_path': self.picture.pk,
            'age': self.age,
            'gender': dict(GENDERS)[self.gender],
            'rect': {
                'top': self.rect_top,
                'left': self.rect_left,
                'width': self.rect_width,
                'height': self.rect_height
            },
            'person': self.person.name if self.person is not None else ''
        }
