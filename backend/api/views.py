import io

from django.contrib.auth import get_user_model
from django.db.models import F, Q, Sum
from django.http import FileResponse
from django.utils import timezone
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    DjangoModelPermissions,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.constant import ONE_TRUE_CONST, ZERO_FALSE_CONST
from api.filters import IngredientFilter
from api.mixins import GetPostDeleteMixin
from api.paginators import PageLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteCartRecipeSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSubscribeSerializer,
)
from recipes.models import Carts, Favorites, Ingredient, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter


class UserViewSet(DjoserUserViewSet, GetPostDeleteMixin):
    pagination_class = PageLimitPagination
    permission_classes = (DjangoModelPermissions,)

    @action(
        methods=(
            "GET",
            "POST",
            "DELETE",
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        return self.get_post_delete(
            id, Subscriptions, UserSubscribeSerializer, Q(author__id=id)
        )

    @action(
        methods=("GET",),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet, GetPostDeleteMixin):
    queryset = Recipe.objects.select_related("author")
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = PageLimitPagination

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.getlist("tags")
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        author = self.request.query_params.get("author")
        if author:
            queryset = queryset.filter(author=author)
        if self.request.user.is_anonymous:
            return queryset

        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        if is_in_shopping_cart in ONE_TRUE_CONST:
            queryset = queryset.filter(in_carts__user=self.request.user)
        elif is_in_shopping_cart in ZERO_FALSE_CONST:
            queryset = queryset.exclude(in_carts__user=self.request.user)

        is_favorited = self.request.query_params.get("is_favorited")
        if is_favorited in ONE_TRUE_CONST:
            queryset = queryset.filter(in_favorites__user=self.request.user)
        if is_favorited in ZERO_FALSE_CONST:
            queryset = queryset.exclude(in_favorites__user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.request.method in ("GET",):
            return RecipeGetSerializer
        return RecipeSerializer

    @action(
        methods=(
            "GET",
            "POST",
            "DELETE",
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        return self.get_post_delete(
            pk, Favorites, FavoriteCartRecipeSerializer, Q(recipe__id=pk)
        )

    @action(
        methods=(
            "GET",
            "POST",
            "DELETE",
        ),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        return self.get_post_delete(
            pk, Carts, FavoriteCartRecipeSerializer, Q(recipe__id=pk)
        )

    @action(
        methods=("GET",),
        detail=False,
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            Ingredient.objects.filter(recipe__recipe__in_carts__user=user)
            .values("name", measurement=F("measurement_unit"))
            .annotate(amount=Sum("recipe__amount"))
        )

        font = "Montserrat-SemiBold"
        pdfmetrics.registerFont(
            TTFont("Montserrat-SemiBold", "Montserrat-SemiBold.ttf", "UTF-8")
        )
        buffer = io.BytesIO()
        pdf_file = canvas.Canvas(buffer)
        pdf_file.setFont(font, 16)
        date_now = timezone.localtime(timezone.now())
        pdf_file.drawString(
            50,
            800,
            f"{date_now.strftime('%d/%m/%Y %H:%M')}",
        )

        pdf_file.drawString(50, 750, f"Список покупок для: {user.first_name}")
        pdf_file.setFont(font, 14)
        from_bottom = 700
        for ingredient in ingredients:
            pdf_file.drawString(
                50,
                from_bottom,
                (
                    f"{ingredient['name']}: "
                    f"{ingredient['amount']} {ingredient['measurement']}"
                ),
            )
            from_bottom -= 20
            if from_bottom <= 50:
                from_bottom = 700
                pdf_file.showPage()
                pdf_file.setFont(font, 14)
        pdf_file.showPage()
        pdf_file.save()
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename=f"{user.username}_shopping_list.pdf",
        )
