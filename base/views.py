from rest_framework.decorators import api_view, permission_classes,parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from base.models import Blog, User, Gallery, Document
from base.serializers import BlogSerializer, UserSerializerWithToken, UserSerializer, TeamsSerializer, GallerySerializer, DocumentSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.http import FileResponse
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import EmailMultiAlternatives



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    



from rest_framework import status


@api_view(['POST'])
def register(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    number = data.get('mobile')
    image = data.get('image')

    # Check if username exists
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email exists
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if number exists
    if User.objects.filter(mobile_number=number).exists():
        return Response({'error': 'Mobile number already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Create new user if all checks pass
    try:
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            mobile_number=number
        )

        if image:
            user.image = image
            user.save()

        serializer = UserSerializerWithToken(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






@api_view(['POST'])
def request_forget_password(request):
    email = request.data.get('email')
    user = User.objects.filter(email=email).first()
    
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializerWithToken(user, many=False)
    token = serializer.data.token
    
    subject = 'Password Reset Link'
    html_message = f'<p>Your password reset link is: <a href="https://frontend.com/resetpassword?token={token}">Click here to reset your password</a></p>'
    
    email_message = EmailMultiAlternatives(
        subject,
        '',
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    email_message.attach_alternative(html_message, "text/html")
    
    email_message.send(fail_silently=False)
    
    return Response({'message': 'Password reset link sent successfully'}, status=status.HTTP_200_OK)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request):
    user = request.user
    data = request.data
    new_password = data.get('new_password')
    user.password = make_password(new_password)
    user.save()
    return Response({"message":"Password reset successfully"})
    
    





@api_view(['GET'])
def BlogListAdmin(request):
    blog = Blog.objects.all()
    serializer = BlogSerializer(blog, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def BlogList(request):
    blog = Blog.objects.filter().order_by("-publish_date")
    serializer = BlogSerializer(blog, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def createBlog(request):
    data = request.data
    blog= Blog.objects.create(
        author = request.user,
        title=data.get('title'),
        featured_image= data.get('image'),
        category=data.get('category'),
        content = data.get('content')
    ) 
    return Response(BlogSerializer(blog).data)

    
@api_view(['GET'])
def BlogDetails(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        blog.views += 1
        blog.save()
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = BlogSerializer(blog, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def BlogDetailsNoCount(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = BlogSerializer(blog, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateBlog(request, id):
    try:
        blog = Blog.objects.get(id=id)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

   
    data = request.data

    # Update title and content
    blog.title = data.get('title', blog.title)
    blog.content = data.get('content', blog.content)
    blog.category = data.get('category', blog.category)
    if 'published' in data:
        blog.published = data['published'] in [True, 'true', 'True', '1']
    else:
        blog.published = False
   
   

    # Check if image data is provided
    if 'image' in request.FILES:
        blog.featured_image = request.FILES['image']
    else:
        # Optionally handle the case when no image is provided
        pass

    blog.save()

    serializer = BlogSerializer(blog, many=False)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteBlog(request, id):
    try:
        blog = Blog.objects.get(id=id)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    #if request.user.profile != blog.author:
    #    return Response({'message': 'You do not have permission to delete this blog'}, status=status.HTTP_403_FORBIDDEN)

    blog.delete()
    return Response({'message': 'Blog deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


from base.models import Teams

@api_view(['GET'])
def TeamList(request):
    teams = Teams.objects.all()
    serializer = TeamsSerializer(teams, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_team_by_id(request,pk):
    team = Teams.objects.get(id=pk)
    serializer = TeamsSerializer(team)
    return Response(serializer.data)


# @api_view(["POSt"])
# @permission_classes([IsAuthenticated])
# def add_image(request):
#     data = request.data
#     serializer = GallerySerializer(data=data, patial=True)
#     if serializer.is_valid:
#         serializer.save()



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_image(request):
    data = request.data
    image = data.get("image")
    description = data.get("description")
    upload = Gallery.objects.create(
        image=image,
        description=description
    )
    serializer = GallerySerializer(upload, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_image(request,id):
    data = request.data
    gallery = Gallery.objects.get(id=id)
    gallery.image = data.get("image")
    gallery.description = data.get("description")
    gallery.save()
    
    serializer = GallerySerializer(gallery, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def get_images(request):
    images = Gallery.objects.all()
    serializer = GallerySerializer(images, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_image(request,id):
    image = Gallery.objects.get(id=id)
    serializer = GallerySerializer(image, many=False)
    return Response(serializer.data)



@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_image(request,id):
    gallery = Gallery.objects.get(id=id)
    gallery.delete()
    return Response({"message":"Gallery deleted"})


class DocumentPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


@api_view(['GET'])
def get_documents(request):
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    
    documents = Document.objects.all().order_by('-uploaded_at')
    
    if search:
        documents = documents.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(file_type__icontains=search)
        )
    if category and category.lower() != 'all':
        documents = documents.filter(category__iexact=category)
        
    paginator = DocumentPagination()
    page = paginator.paginate_queryset(documents, request)
    if page is not None:
        serializer = DocumentSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
        
    serializer = DocumentSerializer(documents, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def get_document(request, id):
    try:
        document = Document.objects.get(id=id)
        serializer = DocumentSerializer(document, many=False, context={'request': request})
        return Response(serializer.data)
    except Document.DoesNotExist:
        return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_document(request):
    data = request.data
    file = request.FILES.get('file')
    if not file:
        return Response({'detail': 'A document file is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
    title = data.get('title')
    if not title:
        return Response({'detail': 'Title is required.'}, status=status.HTTP_400_BAD_REQUEST)

    document = Document.objects.create(
        title=title,
        description=data.get('description', ''),
        category=data.get('category', 'General') or 'General',
        file=file,
        uploaded_by=request.user if request.user.is_authenticated else None
    )
    serializer = DocumentSerializer(document, many=False, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_document(request, id):
    try:
        document = Document.objects.get(id=id)
    except Document.DoesNotExist:
        return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    if 'title' in data:
        document.title = data.get('title')
    if 'description' in data:
        document.description = data.get('description')
    if 'category' in data:
        document.category = data.get('category') or 'General'
    if 'file' in request.FILES:
        document.file = request.FILES['file']
        
    document.save()
    serializer = DocumentSerializer(document, many=False, context={'request': request})
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, id):
    try:
        document = Document.objects.get(id=id)
    except Document.DoesNotExist:
        return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

    if document.file:
        try:
            document.file.delete(save=False)
        except Exception:
            pass
    document.delete()
    return Response({'message': 'Document deleted successfully'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def download_document(request, id):
    try:
        document = Document.objects.get(id=id)
    except Document.DoesNotExist:
        return Response({'detail': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
    document.download_count += 1
    document.save(update_fields=['download_count'])
    
    import os
    if document.file:
        try:
            if os.path.exists(document.file.path):
                response = FileResponse(
                    open(document.file.path, 'rb'),
                    as_attachment=True,
                    filename=os.path.basename(document.file.name)
                )
                return response
        except Exception:
            pass
        from django.shortcuts import redirect
        return redirect(document.file.url)
    return Response({'detail': 'File not found on disk'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_document_categories(request):
    categories = Document.objects.values_list('category', flat=True).distinct()
    unique_categories = sorted(list(set(c.strip() for c in categories if c and c.strip())))
    return Response(unique_categories)