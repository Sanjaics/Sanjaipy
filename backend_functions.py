import streamlit_authenticator as stauth
import model

def create_new_user(username, name, password, age, gender, email_id, phone):
    password = stauth.Hasher([password]).generate()[0]
    user = model.User(user_id=username, name=name, password=password, age=age, gender=gender, email_id=email_id, phone=phone)
    user.save()
