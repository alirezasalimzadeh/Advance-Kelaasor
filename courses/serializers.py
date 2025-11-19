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


# -------------------- GROUP PRICING --------------------


class GroupPricingSerializer(serializers.ModelSerializer):
    """Serializer for group pricing tiers."""

    class Meta:
        model = models.GroupPricing
        fields = '__all__'


# -------------------- COURSE EDITION --------------------


class CourseEditionSerializer(serializers.ModelSerializer):
    """Serializer for course editions (online/offline)."""
    course = serializers.StringRelatedField(read_only=True)
    instructors = serializers.StringRelatedField(many=True, read_only=True)
    group_pricings = GroupPricingSerializer(many=True, read_only=True)

    seats_taken = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.CourseEdition
        fields = '__all__'



