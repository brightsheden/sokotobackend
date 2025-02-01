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
    path('gallery/add_image/', add_image, name='add_image'),
    path('gallery/update_image/<int:id>/', update_image, name='update_image'),
    path('gallery/get_images/', get_images, name='get_images'),
    path('gallery/delete_image/<int:id>/', delete_image, name='delete_image'),
    path('gallery/get_image/<str:id>/', get_image)
]
