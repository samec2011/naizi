from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)


class GetPostDeleteMixin:
    def get_post_delete(self, pk, linked_model, serializ, q):
        obj = get_object_or_404(self.queryset, id=pk)
        serializer = serializ(
            obj,
            context={"request": self.request},
        )
        linked_obj = linked_model.objects.filter(q & Q(user=self.request.user))
        linked_obj_exists = linked_obj.exists()
        if (self.request.method in ("POST",)) and not linked_obj_exists:
            linked_model(None, obj.id, self.request.user.id).save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        if (self.request.method in ("DELETE",)) and linked_obj_exists:
            linked_obj[0].delete()
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)
