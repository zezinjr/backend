from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from account import managers


class GlobalPermissions(models.Model):
    class Meta:
        managed = False
        permissions = (
        )


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        db_column='tx_username',
        null=False,
        max_length=64,
        unique=True
    )
    password = models.CharField(
        db_column='tx_password',
        null=False,
        max_length=104,
    )
    name = models.CharField(
        db_column='tx_name',
        null=True,
        max_length=256
    )
    email = models.CharField(
        db_column='tx_email',
        null=True,
        max_length=256
    )
    last_login = models.DateTimeField(
        db_column='dt_last_login',
        null=True
    )
    is_active = models.BooleanField(
        db_column='cs_active',
        null=False,
        default=True
    )
    is_superuser = models.BooleanField(
        db_column='cs_superuser',
        null=True,
        default=False
    )
    is_staff = models.BooleanField(
        db_column='cs_staff',
        null=True,
        default=False
    )
    is_default = models.BooleanField(
        db_column='cs_default',
        null=True,
        default=False
    )
    avatar = models.BinaryField(
        db_column='bl_avatar',
        null=True
    )
    is_ad_user = models.BooleanField(
        db_column='cs_is_ad_user',
        null=False,
        default=False
    )
    is_privileged_user = models.BooleanField(
        db_column='cs_is_privileged_user',
        null=True,
    )

    groups = models.ManyToManyField(
        Group,
        through='AccountUserGroup',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='user_set',
        related_query_name="user",
    )

    objects = managers.UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']


class AccountUserGroup(models.Model):
    id = models.BigAutoField(
        db_column='id',
        primary_key=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column='id_user',
        related_name='account_user_groups',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.DO_NOTHING,
        db_column='id_group',
        related_name='account_user_groups',
    )

    class Meta:
        managed = True
        db_table = 'account_user_groups'


class Module(models.Model):
    id = models.BigAutoField(
        db_column='id',
        primary_key=True
    )
    description = models.CharField(
        db_column='tx_description',
        max_length=64,
        unique=True,
        blank=True,
        null=True,
    )
    icon = models.CharField(
        db_column='tx_icon',
        max_length=64,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        db_column='cs_active',
        null=False,
        default=True,
    )
    menu = models.BooleanField(
        db_column='cs_menu',
        null=True,
        default=True,
    )

    def __str__(self):
        return self.description

    class Meta:
        managed = True
        db_table = 'account_module'
        permissions = (
            ('load_module', 'Can load module'),
        )


class Menu(models.Model):

    class TypeIcon(models.TextChoices):
        DEFAULT = 'material-icons', _('Material Icons')
        OUTLINED = 'material-icons-outlined', _('Material Icons Outlined')
        ROUND = 'material-icons-round', _('Material Icons Round')
        SHEET = 'material-icons-sharp', _('Material Icons Sharp')
        TWO = 'material-icons-two', _('Material Icons Two Tone')

    id = models.BigAutoField(
        db_column='id',
        primary_key=True
    )
    description = models.CharField(
        db_column='tx_description',
        max_length=64,
        blank=True,
        null=True,
    )
    icon = models.CharField(
        db_column='tx_icon',
        max_length=64,
        blank=True,
        null=True,
    )
    font_set = models.CharField(
        db_column='tx_font_set',
        max_length=64,
        null=False,
        choices=TypeIcon.choices,
        default=TypeIcon.DEFAULT,
    )
    route = models.CharField(
        db_column='tx_route',
        max_length=64,
        blank=True,
        null=True,
    )

    def __str__(self):
        return '%s - %s' % (self.description, self.route)

    class Meta:
        managed = True
        db_table = 'account_menu'


class ModuleMenu(models.Model):
    root = models.ForeignKey(
        'Menu',
        on_delete=models.CASCADE,
        db_column='id_root',
        related_name='menus',
        null=True,
    )
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        db_column='id_module',
        related_name='module_menus',
        null=False,
    )
    menu = models.ForeignKey(
        'Menu',
        on_delete=models.CASCADE,
        db_column='id_menu',
        related_name='module_menus',
        null=False,
    )
    order = models.IntegerField(
        db_column='nb_order',
        null=True,
    )
    has_divider = models.BooleanField(
        db_column='cs_divisor',
        null=False,
        default=False,
    )
    is_active = models.BooleanField(
        db_column='cs_active',
        null=False,
        default=True,
    )

    def __str__(self):
        return '%s - %s' % (self.module.description, self.menu.description)

    class Meta:
        managed = True
        db_table = 'account_module_menu'
        unique_together = (['module', 'menu'])
        permissions = (
            ('load_module_menu', 'Can load module menu'),
        )


class LoggedInUser(models.Model):
    user = models.ForeignKey(User, related_name="logged_in_user", on_delete=models.CASCADE)
    last_token = models.CharField(max_length=10000, null=True, blank=True)
    created_at = models.DateTimeField(
        db_column="dt_created",
        auto_now_add=True,
        null=False,
    )

    class Meta:
        managed = True
        db_table = 'account_logged_in_user'

    def __str__(self):
        return self.user.username


class GroupExtraFields(models.Model):
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        db_column='id_group',
        related_name='group_extra_fields',
    )

    code = models.CharField(
        db_column='tx_code',
        null=False,
        blank=False,
        unique=True,
        max_length=64
    )

    class Meta:
        managed = True
        db_table = 'group_extra_fields'


class GroupProxy(Group):
    objects = managers.GroupManager()

    class Meta:
        proxy = True
        managed = False
