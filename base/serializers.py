from rest_framework import serializers
from .models import *
                    

from rest_framework_simplejwt.tokens import RefreshToken
import bleach





class UserSerializer(serializers.ModelSerializer):

   
    isAdmin = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User 
        fields = ['id','username','mobile_number','image', 'email',"isAdmin",]

    
    def get_isAdmin(self,obj):
        return obj.is_staff



class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username','email',"isAdmin", 'token']

    def get_token(self, obj):
        token =RefreshToken.for_user(obj)
        return str(token.access_token)



class BlogSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = Blog
        fields = "__all__"
        read_only_fields = ['author_name']

    def get_author_name(self, obj):
        return obj.author.username  # Adjust based on your Profile model's name field

    def validate_content(self, value):
        # Sanitize the HTML content and strip all tags to convert to plain text
        allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + ['img', 'p', 'h2', 'h3', 'h4', 'blockquote', 'ul', 'ol', 'li']
        allowed_attributes = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
        allowed_attributes.update({'img': ['src', 'alt']})

        # First, clean the HTML to keep only the allowed tags
        sanitized_html = bleach.clean(value, tags=allowed_tags, attributes=allowed_attributes)

        # Then, strip all tags to convert it to plain text
        plain_text = bleach.clean(sanitized_html, tags=[], strip=True)

        return plain_text

    def create(self, validated_data):
        validated_data['content'] = self.validate_content(validated_data.get('content', ''))
        return super().create(validated_data)
    


class TeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ['id', 'name', 'image', 'position']
        read_only_fields = ['id']

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'