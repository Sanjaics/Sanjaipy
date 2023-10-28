from django.db import models

# Create your models here.


class User(models.Model):
    user_id = models.CharField('User Id', max_length=50, primary_key=True)
    name = models.CharField('Name', max_length=50)
    age = models.IntegerField('Age', blank=True, null=True)
    gender = models.CharField('Gender', max_length=50)
    email_id = models.EmailField('Email Id', max_length=254)
    phone = models.CharField('Phone Number', max_length=50)
    password = models.CharField("Password", max_length=100)
    # entries
    # characters

    def __str__(self):
        return str(self.name)


class Entry(models.Model):
    entry_id = models.AutoField('Entry Id', primary_key=True)
    day_explanation = models.TextField('Day Explanation', max_length=5000)
    over_all_sentiment_score = models.DecimalField(
        'Over All Sentiment Score', max_digits=10, decimal_places=5, blank=True, null=True)
    day_type = models.CharField('Day Type', max_length=50)
    date = models.DateField('Date', auto_now=True, auto_now_add=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='entries')
    # occurences

    def __str__(self):
        return str(self.entry_id)


class Character(models.Model):
    character_id = models.AutoField('Character Id', primary_key=True)
    name = models.CharField('Name', max_length=50)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='characters')
    # occurences

    def __str__(self):
        return str(self.name)


class Occurence(models.Model):
    occurence_id = models.AutoField('Occurence Id', primary_key=True)
    impact_type = models.CharField('Imapct Type', max_length=50)
    sentiment_score = models.DecimalField(
        'Sentiment Score', max_digits=10, decimal_places=5)
    entry = models.ForeignKey(
        Entry, on_delete=models.CASCADE, related_name='occurences')
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name='occurences')

    def __str__(self):
        return str(self.occurence_id)
