from django import forms


class GuessForm(forms.Form):
    guess = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control col-sm-4",
            "placeholder": "Proposition",
            "maxlength": 50,
            "minlength": 0,
            "autocomplete": "off",
        })
    )

    def __init__(self, longueur):
        super().__init__()
        self.fields['guess'].widget.attrs.update({
            "maxlength": longueur,
            "minlength": longueur,
        })




