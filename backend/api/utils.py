from recipes.models import AmountIngredient, Ingredient


def amount_ingredient_create(recipe, ingredients):
    amount_ingredient = []

    for ingredient in ingredients:
        amount_ingredient.append(
            AmountIngredient(
                recipe=recipe,
                ingredients=Ingredient.objects.get(pk=ingredient["id"]),
                amount=ingredient["amount"],
            )
        )

    AmountIngredient.objects.bulk_create(amount_ingredient)
