import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Chat(models.Model):
    participants = models.ManyToManyField(User)
    time_create = models.DateTimeField(auto_now_add=True)


def groups_directory_path(instance, filename):
    return os.path.join('uploads', f'groups', 'group_avatar.jpg')


class Group(models.Model):
    root = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to=groups_directory_path, default='default_group_avatar.jpg')
    bio = models.TextField(max_length=255, default='No bio')
    participants = models.ManyToManyField(User, related_name='participant_groups')
    admins = models.ManyToManyField(User, related_name='admin_groups')
    time_create = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'root'

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Group.objects.get(pk=self.pk)
            if old_instance.avatar != self.avatar and old_instance.avatar != 'default_group_avatar.jpg':
                old_instance.avatar.delete(save=False)
        super(Group, self).save(*args, **kwargs)


class Messages(models.Model):
    message_type = models.TextField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    chat_id = models.IntegerField()


class GroupMessages(models.Model):
    message_type = models.TextField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    chat_id = models.IntegerField()


def user_directory_path(instance, filename):
    user_id = instance.user.id
    return os.path.join('uploads', f'user_{user_id}', 'avatar.jpg')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, default='default_avatar.jpg')
    bio = models.TextField(max_length=255, blank=True, default='No bio')
    last_online = models.DateTimeField(auto_now=True, blank=True, null=True)
    status_online = models.BooleanField(blank=True, default=False)

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Profile.objects.get(pk=self.pk)
            if old_instance.avatar != self.avatar and old_instance.avatar != 'default_avatar.jpg':
                old_instance.avatar.delete(save=False)
        super(Profile, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
