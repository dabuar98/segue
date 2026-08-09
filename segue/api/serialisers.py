from rest_framework import serializers
from app.models import Tracks

class TrackSerialiser(serializers.ModelSerializer):
    subgenres = serializers.SlugRelatedField(
        source='genres', many=True, read_only=True, slug_field='genre'
    )

    class Meta:
        model = Tracks
        fields = ['mbid', 'title', 'artist', 'album', 'date', 'subgenres']
