from django.db import models

class Election(models.Model):
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_open = models.BooleanField(default=False)
    show_results = models.BooleanField(default=False)  # KPU trigger manual

    def __str__(self):
        return f"Election {self.year}"

class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=200)
    vision = models.TextField(blank=True)
    poster = models.ImageField(upload_to='candidates/', blank=True, null=True)
    poster_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class VoterToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='voter_tokens')
    used = models.BooleanField(default=False)
    emailed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email', 'election'], name='uniq_email_per_election')
        ]

class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='votes')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes')
    email = models.EmailField()  # redundansi untuk audit sederhana
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('election', 'email')  # satu kali vote per email

class FraudReport(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    