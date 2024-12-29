# TODO There's certainly more than one way to do this task, so take your pick.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Post
from .serializers import PostSerializer
import random

# class PostListView(generics.ListAPIView):
#     queryset = Post.objects.all().order_by('-timestamp')
#     serializer_class = PostSerializer

class PostListView(APIView):
    def get(self,request, *args, **kwargs):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        posts = Post.objects.all().order_by('-timestamp')
        paginated_posts = paginator.paginate_queryset(posts, request)
        serialized_posts = PostSerializer(paginated_posts, many=True)
        return paginator.get_paginated_response(serialized_posts.data)
    
# for random comments
def random_comments(post, count = 3):
    comments = post.comments.all()
    if comments.count() > count:
        comments = random.sample(list(comments), count)
    return comments
