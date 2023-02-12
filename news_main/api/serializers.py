from rest_framework import serializers

from news_output.models import News, Comment, Rubric

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id', 'title', 'description', 'author', 'published')

class NewsDetailSerialzer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id', 'title', 'description', 'author', 'published', 'image')

class CommentSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('news', 'author', 'content', 'created_at')

class RubricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubric
        fields = ('id', 'name')