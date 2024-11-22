from django.urls import path
from base.views import *

urlpatterns = [
   path('auth/login/',MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),

    path('auth/register/', register),
    path('blog/create_blog/', createBlog),
    path('blogs', BlogList),
    path('blog/<slug:slug>/', BlogDetails),
    path('blog/update/<str:id>/', updateBlog),
    path('blog/delete/<str:id>/', deleteBlog),
]
