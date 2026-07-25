from django.db import models

# Define model for Subgenres table
class Subgenres(models.Model):
    mb_id = models.CharField(max_length=250, null=False, blank=False)
    genre = models.CharField(max_length=250, null=False, blank=False)

    def __str__(self):
        return self.genre

    
    class Meta:
        # Define index on Music Brainz ID to speed up retrieval
        indexes = [
            models.Index(fields=['mb_id'])
        ]

        # Prevent duplicates
        constraints = [
            models.UniqueConstraint(fields=['mb_id', 'genre'], name='unique_track_genre')
        ]

# Define model for Tracks table
class Tracks(models.Model):
    mb_id = models.CharField(max_length=250, null=False, blank=False)
    title = models.CharField(max_length=250, null=False, blank=False)
    artist = models.CharField(max_length=250, null=False, blank=False)
    album = models.CharField(max_length=250, null=False, blank=False)
    date = models.CharField(max_length=250, null=False, blank=False)
    genres = models.ManyToManyField(Subgenres, through='TrackSubgenreLink')

    def __str__(self):
        return self.title

    # Define index on Music Brainz ID to speed up retrieval
    class Meta:
        indexes = [
            models.Index(fields=['mb_id'])
        ]

# Define junction table
class TrackSubgenreLink(models.Model):
    track = models.ForeignKey(Tracks, on_delete=models.CASCADE)
    subgenre = models.ForeignKey(Subgenres, on_delete=models.CASCADE)