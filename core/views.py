from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponseNotFound, HttpResponse
import time
import requests
import os
import json
from .models import DetectedFace, Person, GENDERS, Picture


detect_url = 'https://api.projectoxford.ai/face/v1.0/detect'
group_url = 'https://api.projectoxford.ai/face/v1.0/group'
similar_url = 'https://api.projectoxford.ai/face/v1.0/findsimilars'
_key = 'bcf4e91ae0284abbbdb5d77dcaa56984' #Here you have to paste your primary key
_maxNumRetries = 10


def processRequest(json, data, headers, params, url=detect_url, method='post'):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request(method, url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['error']['message']))

        break

    return result


def get_gender(gender_text):
    return 0 if gender_text == 'male' else 1


def detect_faces(batch_number):
    d = r'C:\Code\faces\FershtmanPics\Assorted\\' + str(batch_number)

    fns = os.listdir(d)
    for i, fn in enumerate(fns):
        pathToFileInDisk = d + '\\' + fn
        with open(pathToFileInDisk, 'rb') as f:
            data = f.read()

        print("\r[{}/{}] {: <40}".format(i + 1, len(fns), fn), end='')

        # Face detection parameters
        params = {'returnFaceAttributes': 'age,gender',
                  'returnFaceLandmarks': 'false'}

        headers = dict()
        headers['Ocp-Apim-Subscription-Key'] = _key
        headers['Content-Type'] = 'application/octet-stream'

        json = None

        result = processRequest(json, data, headers, params)

        if result:
            p = Picture(pk=pathToFileInDisk)
            p.save()

            for r in result:
                try:
                    f = DetectedFace(pk=r['faceId'],
                                     picture=p,
                                     age=r['faceAttributes']['age'],
                                     gender=get_gender(r['faceAttributes']['gender']),
                                     rect_top=r['faceRectangle']['top'],
                                     rect_left=r['faceRectangle']['left'],
                                     rect_width=r['faceRectangle']['width'],
                                     rect_height=r['faceRectangle']['height'])
                    f.save()
                except Exception as e:
                    print("Exception: ", e)
        time.sleep(0.5)


def index(request):
    return render(request, 'index.html', {'pictures': Picture.objects.all(), 'people': Person.objects.all()})


@csrf_exempt
def get_faces(request):
    pic_path = request.GET['pic_id'].replace('Pics', r'C:\Code\faces\FershtmanPics').replace('/', '\\')
    try:
        pic = Picture.objects.get(pk=pic_path)
    except Picture.DoesNotExist:
        return HttpResponseNotFound()

    faces = [d.to_dict() for d in pic.detectedface_set.all()]
    return HttpResponse(json.dumps(faces))


@csrf_exempt
def update_face(request):
    try:
        f = DetectedFace.objects.get(pk=request.POST['face_id'])
        f.person = Person.objects.get(pk=request.POST['person'])
    except (KeyError, DetectedFace.DoesNotExist, Person.DoesNotExist):
        return HttpResponseNotFound()

    f.save()
    return HttpResponse()
