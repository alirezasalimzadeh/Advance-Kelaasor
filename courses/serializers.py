from rest_framework import serializers
from courses import models


# -------------------- CATEGORY --------------------

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for course categories."""
    children = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'


# -------------------- COURSE MEDIA --------------------

class CourseMediaSerializer(serializers.ModelSerializer):
    """Serializer for course media assets."""
    class Meta:
        model = models.CourseMedia
        fields = '__all__'

# -------------------- COURSE --------------------

class CourseSerializer(serializers.ModelSerializer):
    """Serializer for courses with category and media."""
    category = CategorySerializer(read_only=True)
    media = CourseMediaSerializer(many=True, read_only=True)

    class Meta:
        model = models.Course
        fields = '__all__'



