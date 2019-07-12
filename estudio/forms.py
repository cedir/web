from django import forms


class EstudioAdminForm(forms.ModelForm):
    def full_clean(self):
        super(EstudioAdminForm, self).full_clean()
        # TODO: Valudate fecha estudio
        # TODO: por algun motivo a pesar del raise, guardaa igual
        # TODO: falta testear que no se este rompiendo algo
        if self.current_user.groups.filter(name__icontains='Medicos').exists():
            raise forms.ValidationError("El estudio ha expirado y no puede modificarse")
