from django import forms
from .models import table
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from . models import Products


class Signupform(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    confirm_password=forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = table
        fields = ('username', 'email', 'password', 'confirm_password')

    # user check

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if table.objects.filter(username=username).exists():
            raise forms.ValidationError("username already exists")
        return username
        
    # email check    

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if table.objects.filter(email=email).exists():
            raise forms.ValidationError("email already exists")
        return email
        
    # pass rules check

    def clean(self):
        data=super().clean()
        password=data.get('password')
        confirm=data.get('confirm_password')

        if password and confirm and  password !=confirm:
            self.add_error('confirm_password',"Password do not match")
        
        if password:        
            if len(password) < 8:
              self.add_error('password',"Password must be at least 8 characters")    

            if password.isdigit():
              self.add_error('password',"Password cannot be fully numeric") 

        return data


        # hash pass   

    def save(self, commit =True):
        user= super().save(commit=False)
        user.password=make_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
        return user    
    


class Loginform(forms.Form):
    login=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
'placeholder':' username or email'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
'placeholder':' password'}))

    def clean(self):
        data = super().clean()
        login_input = data.get('login')
        password = data.get('password')

        if login_input and password:
            # Find user by username or email
            user = table.objects.filter(username=login_input).first() or table.objects.filter(email=login_input).first()
            
            if not user:
                raise forms.ValidationError("User does not exist")
            
            if not user.is_active:
                raise forms.ValidationError("this user is blocked")
            
            # Check password
            auth_user = authenticate(username=user.username, password=password)
            if not auth_user:
                raise forms.ValidationError("Incorrect password")
            
            # Attach user for use in views
            self.user = auth_user

        return data





class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'price', 'description', 'image1','image2','image3','image','stock','discount_price','discount_percentage',]
