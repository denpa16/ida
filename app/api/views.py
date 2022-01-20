from rest_framework import viewsets
from .models import Image
from .serializers import ImageSerializer
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from PIL import Image as Im
import requests
from django.core.files.base import ContentFile


class ImageViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = Image.objects.all()
        serializer = ImageSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Image.objects.all()
        image = get_object_or_404(queryset, pk=pk)
        serializer = ImageSerializer(image)
        return Response(serializer.data)

    def create(self, request):
        #save image from local storage
        if request.FILES:
            serializer = ImageSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            saved_image = get_object_or_404(Image.objects.all(), pk=serializer.instance.pk)
            saved_image.name = serializer.instance.picture.url.split('/')[-1]
            saved_image.width, saved_image.height = Im.open(serializer.instance.picture).size
            saved_image.save()
            return Response(ImageSerializer(saved_image).data)
        #save image from url
        if request.data['url']:
            response = requests.get(request.data['url']) 
            image = Image()
            image.picture.save(request.data['url'].split('/')[-1], ContentFile(response.content), save=True)
            image.height, image.width = Im.open(image.picture).size
            image.name = image.picture.url.split('/')[-1]
            image.url = request.data['url']
            image.save()
            return Response(ImageSerializer(image).data)

    def destroy(self, request, pk=None):
        image = get_object_or_404(Image.objects.all(), pk=pk)
        image.delete()
        return Response()


class ImageResizeViewSet(viewsets.ViewSet):

    def create(self, request, pk=None):
        parent_image = get_object_or_404(Image.objects.all(), pk=pk)
        old_picture = Im.open(parent_image.picture)
        old_width, old_height = old_picture.size
        resized_image = Image()
        if '_' in parent_image.picture.url:
            origin_name = parent_image.picture.url.split('_')[-1]
        else:
            origin_name = parent_image.picture.url.split('/')[-1]
        if ('width' in request.data) and ('height' not in request.data):
            new_picture = old_picture.resize((int(request.data['width']),old_height), Im.ANTIALIAS)
            resized_image.width = int(request.data['width'])
            resized_image.height = old_height
            new_picture.save('media/images/width-{}_{}'.format(request.data['width'], origin_name))
            resized_image.name = 'width-{}_{}'.format(request.data['width'], origin_name)

        if ('width' not in request.data) and ('height' in request.data):
            new_picture = old_picture.resize((old_width, int(request.data['height'])), Im.ANTIALIAS)
            a = new_picture
            resized_image.height = int(request.data['height'])
            resized_image.width = old_width
            new_picture.save('media/images/height-{}_{}'.format(request.data['height'], origin_name))
            resized_image.name = 'height-{}_{}'.format(request.data['height'], origin_name)

        if ('width' in request.data) and ('height' in request.data):
            new_picture = old_picture.resize((int(request.data['width']), int(request.data['height'])), Im.ANTIALIAS)
            resized_image.height = int(request.data['height'])
            resized_image.width = int(request.data['width'])
            new_picture.save('media/images/height-{}-width-{}_{}'.format(request.data['height'], request.data['width'], origin_name))
            resized_image.name = 'height-{}-width-{}_{}'.format(request.data['height'], request.data['width'], origin_name)

        resized_image.picture = 'images/{}'.format(resized_image.name)
        resized_image.parent_picture = parent_image.id
        resized_image.url = parent_image.url
        resized_image.save()
        return Response(ImageSerializer(resized_image).data)