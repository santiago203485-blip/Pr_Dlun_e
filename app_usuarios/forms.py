from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class RegistroForm(UserCreationForm):
    """Registro de clientes desde la tienda en línea."""

    first_name = forms.CharField(label='Nombres', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    telefono = forms.CharField(label='Teléfono (WhatsApp)', max_length=20)

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono')
        labels = {'username': 'Nombre de usuario'}

    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'foto')
        labels = {'first_name': 'Nombres', 'last_name': 'Apellidos', 'email': 'Correo'}


class UsuarioAdminForm(forms.ModelForm):
    """Formulario del administrador para crear/editar empleados."""

    password = forms.CharField(
        label='Contraseña', widget=forms.PasswordInput, required=False, min_length=6,
        help_text='Mínimo 6 caracteres. Déjala vacía para no cambiarla.',
    )

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'telefono', 'rol', 'is_active')
        labels = {
            'username': 'Usuario', 'first_name': 'Nombres', 'last_name': 'Apellidos',
            'email': 'Correo', 'is_active': 'Activo',
        }

    def clean(self):
        datos = super().clean()
        if not self.instance.pk and not datos.get('password'):
            self.add_error('password', 'La contraseña es obligatoria para usuarios nuevos.')
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get('password'):
            usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario
