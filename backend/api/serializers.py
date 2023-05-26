from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    SerializerMethodField,
)

from api.utils import amount_ingredient_create
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag

User = get_user_model()


class FavoriteCartRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = ("__all__",)


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, author):
        user = self.context.get("request").user
        if user.is_anonymous or (user == author):
            return False

        return user.subscriptions.filter(author=author).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSubscribeSerializer(UserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = ("__all__",)

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        serializer = FavoriteCartRecipeSerializer(
            recipes, many=True, read_only=True
        )
        return serializer.data


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )
        read_only_fields = ("__all__",)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )
        read_only_fields = ("__all__",)


class RecipeGetSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            "id", "name", "measurement_unit", amount=F("recipe__amount")
        )

    def get_is_favorited(self, recipe):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context["request"].user

        if user.is_anonymous:
            return False

        return user.carts.filter(recipe=recipe).exists()


class AmountIngredientSerializer(ModelSerializer):
    id = IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ("id", "amount")


class RecipeSerializer(ModelSerializer):
    ingredients = AmountIngredientSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id",)

    def validate(self, data):
        tags = data.get("tags")
        ingredients = data.get("ingredients")
        if not tags:
            raise ValidationError("Нет тегов.")

        if not ingredients:
            raise ValidationError("Нет ингредиентов.")

        ingredients_id = []

        for ingredient in ingredients:
            if not (
                isinstance(ingredient["amount"], int)
                or ingredient["amount"].isdigit()
            ):
                raise ValidationError(
                    "Количество ингредиента указано не верно"
                )

            if ingredient["id"] not in ingredients_id:
                ingredients_id.append(ingredient["id"])
            else:
                raise ValidationError("Ингредиент не должен повторяться")

        db_ingredients = Ingredient.objects.filter(pk__in=ingredients_id)
        if not db_ingredients:
            raise ValidationError("Такого ингредиента не существует")

        return data

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )
        recipe.tags.set(tags)
        amount_ingredient_create(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        super().update(recipe, validated_data)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            amount_ingredient_create(recipe, ingredients)
        return recipe

    def to_representation(self, recipe):
        return RecipeGetSerializer(recipe, context=self.context).data
