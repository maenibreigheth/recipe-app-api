from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from .serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    '''
        Test the publicly available ingredients api
    '''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''
            Test that login is required for retrieving ingredients
        '''

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    '''
        Test the private ingredients api
    '''

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@user.com', 'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        '''
            Test retrieving ingredients
        '''

        Ingredients.objects.create(user=self.user, name='Kale')
        Ingredients.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        '''
            Test that ingredients returned are for the authenticated user
        '''

        user2 = get_user_model().objects.create_user(
            'other@user.com',
            'testpass'
        )

        Ingredient.objects.create(user=user2, name='Fruity')
        user_ingredient = Ingredient.objects.create(
            user=self.user, name='Tomato')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], user_ingredient.name)

    def test_create_ingredient_successful(self):
        '''
            Test creating new ingredient
        '''

        payload = {'name': 'Test ingredient'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid_name(self):
        '''
            Test creating a new tag with invalid payload
        '''

        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
