from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Post, Comment
from rest_framework import status

class PostListTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(text='Test post', user=self.user)

    def test_post_list(self):
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['text'], 'Test post')
        
    def test_post_list_empty(self):
        Post.objects.all().delete()
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])


    def test_post_list_pagination(self):
        for i in range(15):
            Post.objects.create(text=f'Test post {i}', user=self.user)
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['results'][0]['text'], 'Test post 14')
        self.assertEqual(response.data['count'], 16)
        self.assertEqual(response.data['next'], 'http://testserver/posts/?page=2')
        self.assertEqual(response.data['previous'], None)

    def test_post_list_pagination_page_2(self):
        for i in range(15):
            Post.objects.create(text=f'Test post {i}', user=self.user)
        response = self.client.get('/posts/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 6)
        self.assertEqual(response.data['results'][0]['text'], 'Test post 4')
        self.assertEqual(response.data['count'], 16)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], 'http://testserver/posts/')
        
    def test_post_with_comments(self):
        Comment.objects.create(text="Comment 1", post=self.post, user=self.user)
        Comment.objects.create(text="Comment 2", post=self.post, user=self.user)
        Comment.objects.create(text="Comment 3", post=self.post, user=self.user)
        Comment.objects.create(text="Comment 4", post=self.post, user=self.user)

        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comments = response.data['results'][0]['comments']
        
        # Assert the number of comments returned is limited to 3
        self.assertEqual(len(comments), 3)

        self.assertEqual(comments[0]['text'], "Comment 4")  # Latest comment
        self.assertEqual(comments[1]['text'], "Comment 3")
        self.assertEqual(comments[2]['text'], "Comment 2")


    def test_post_list_pagination_invalid_page(self):
        response = self.client.get('/posts/?page=3')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_list_pagination_invalid_page_negative(self):
        response = self.client.get('/posts/?page=-1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_list_pagination_invalid_page_zero(self):
        response = self.client.get('/posts/?page=0')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_list_pagination_invalid_page_string(self):
        response = self.client.get('/posts  /?page=a')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.get('/posts/?page=a')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        
    def test_post_list_pagination_invalid_page_empty_string(self):
        response = self.client.get('/posts/?page=')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

