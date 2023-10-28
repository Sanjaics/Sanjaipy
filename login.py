import datetime
import numpy as np
import matplotlib.pyplot as plt
import july
from july.utils import date_range

# Django Packages
from backend_functions import create_new_user
from django.core.exceptions import MultipleObjectsReturned

# Streamlit Packages
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth

#NLP Functions
from nlp_function import analyze_sentiment,fetch_character_and_text

#Data Manipulation Packages
import pandas as pd

#Django Config
import model

#get score
def get_scores(start: datetime.date, end: datetime.date):
    entries = model.Entry.objects.filter(
        user=model.User.objects.get(user_id=username),
        date__gte=start,
        date__lte=end
    )
    dates = dict()
    while start <= end:
        dates[start.strftime("%Y-%m-%d")] = 0
        start += datetime.timedelta(days=1)
    for entry in entries:
        dates[entry.date.strftime("%Y-%m-%d")] = float(entry.over_all_sentiment_score)
    return dates

#Streamlit Authentication Package
credentials = {"usernames": {}}
users = model.User.objects.all()
for user in users:
    credentials["usernames"][user.user_id] = {
        'email': user.email_id,
        'name': user.name,
        'password': user.password
    }
authenticator = stauth.Authenticate(credentials, 'my_safe_cookie', 'my_safe_cookie_key')
authenticator._check_cookie()

def create_new_user(username, name, password, age, gender, email_id, phone):
    password = stauth.Hasher([password]).generate()[0]
    user = model.User(user_id=username, name=name, password=password, age=age, gender=gender, email_id=email_id, phone=phone)
    user.save()



#Log In Page
st.title("Virtual Journaling App")
if st.session_state.authentication_status != True:
    existing_user_tab,new_user_tab = st.tabs(["Existing User","New User"])

    with existing_user_tab:
        name, authentication_status, username = authenticator.login('login', 'main')
        if authentication_status == False:
            st.error('Username/password is incorrect')
        elif authentication_status == None:
            st.warning('Please enter your username and password')


    with new_user_tab:

        st.write("Hi, Happy to see your here!")
        st.write("Please fill this form to save your precious memories")
        
        with st.form("new_user",clear_on_submit=True):
            name = st.text_input("Name")
            user_name = st.text_input("Username")
            age = st.number_input("Age",step=1)
            gender = st.selectbox("Gender",['Male','Female','Others'])
            email = st.text_input("Email")
            password = st.text_input("Enter Password",placeholder="Atleast 8 Characters....",type='password')
            retype_password = st.text_input("Retype Password",placeholder="Memorize it well...",type='password')
            phone_number = st.text_input("Enter your Phone Number")
            submit = st.form_submit_button("Submit")
            if submit:
                if name and user_name and age and gender and email and password and retype_password and phone_number:
                    if password == retype_password:
                        create_new_user(username=user_name, name=name, password=password, age=age, gender=gender, email_id=email, phone=phone_number)
                        st.write('User Created')
                    else:
                        st.write('Password not matched')
                else:
                    st.write('Fill all fields')
else:
    #Main Page
    authenticator.logout('Logout', 'main')
    username = st.session_state.username
    name = st.session_state.name
    st.write(f"Hi **{name}**.")
    page_select = option_menu(
        menu_title=None,
        options=['Write','Read','Profile'],
        icons=['pencil-square','journal-bookmark','person-badge-fill'],
        default_index=0,
        orientation="horizontal"
    )

    if page_select == 'Write':

        day_explanation = st.text_area('Dear Diary', '''
        Preserve your memories here.....
        ''', height=250)

        submit = st.button('Submit')

        if submit:
            over_all_sentiment_score = analyze_sentiment(day_explanation)
            st.write("Over all sentiment score :",over_all_sentiment_score)
            # get user object
            u = model.User.objects.get(user_id=username)
            # add entry to django database
            e = model.Entry(
                user=u,
                day_explanation=day_explanation,
                day_type='p' if over_all_sentiment_score > 0 else 'n',
                over_all_sentiment_score=over_all_sentiment_score
            )
            e.save()
            character_and_text_data = fetch_character_and_text(day_explanation)
            print(character_and_text_data)
            character_info = []
            for name,statement in character_and_text_data:
                character = dict()
                character['Name'] = name
                character['Statement'] = statement
                character['Sentiment Score'] = analyze_sentiment(statement)
                character_info.append(character)
                # create occurence and character in django database
                c, _ = model.Character.objects.get_or_create(
                    name=name,
                    user=u
                )
                o = model.Occurence(
                    character=c,
                    entry=e,
                    impact_type='p' if character['Sentiment Score'] > 0 else 'n',
                    sentiment_score=character['Sentiment Score']
                )
                o.save()
            print(character_info,"Executed")
            st.table(pd.DataFrame(character_info))
    
    elif page_select == 'Read':
        with st.form('read_form'):
            date = st.date_input("Enter the date :")
            read_submit = st.form_submit_button("View Memory")
            if read_submit:
                try:
                    try:
                        entry = model.Entry.objects.get(date=date, user=username)
                    except MultipleObjectsReturned:
                        entry = list(model.Entry.objects.filter(date=date, user=username))[-1]
                    st.write("Day Explanaton :\n\n", entry.day_explanation)
                    day_type = '<span style="color:green;">Good</span>' if entry.day_type == 'p' else '<span style="color:red;">Bad</span>'
                    st.write("Day Type :", f"It was a {day_type} day.", unsafe_allow_html=True)
                    character_info = []
                    for occurence in entry.occurences.all():
                        impact_type = '<span style="color:green;">Positive</span>' if occurence.impact_type == 'p' else '<span style="color:red;">Negative</span>'
                        character_info.append({
                            'Name': occurence.character.name,
                            'Impact Type': impact_type
                        })
                    st.write(pd.DataFrame(character_info).to_html(escape=False, justify='left'), unsafe_allow_html=True)
                    st.markdown(
                        """
                            <style>
                                table {
                                    width: 100%;
                                }
                            </style>
                        """,
                        unsafe_allow_html=True
                    )
                except model.Entry.DoesNotExist:
                    st.write("No Data Found")

    elif page_select == 'Profile':
        st.markdown(
            """
                <style>
                .big-font {
                    font-size:3rem !important;
                }

                .img {
                position:"absolute",
                width:"6rem",
                height:"6rem",
                }
                </style>
            """, 
            unsafe_allow_html=True
        )
        st.markdown(f'<p class="big-font">Hello {name} !!</p>', unsafe_allow_html=True)
        st.header("Day Type Records")
        entries = model.User(user_id=username).entries.all()
        good_day_container,bad_day_container = st.columns(2,gap="medium")
        with good_day_container:
            st.image('rsz_happy_emoji.png')
            st.write("Happy Stats :", sum(map(lambda entry : entry.day_type == 'p', entries)))
        with bad_day_container:
            st.image('rsz_sad_emoji.png')
            st.write("Sad Stats", sum(map(lambda entry : entry.day_type == 'n', entries)))
        characters = model.User(user_id=username).characters.all()
        character_info = []
        for character in characters:
            character_info.append({
                'Name': character.name,
                'Positive Days': f"{int(sum(map(lambda occurence : occurence.impact_type == 'p', character.occurences.all())) / character.occurences.count() * 100)}%",
                'Negative Days': f"{int(sum(map(lambda occurence : occurence.impact_type == 'n', character.occurences.all())) / character.occurences.count() * 100)}%"
            })

        # present_year = int(datetime.datetime.now().strftime("%Y"))
        # year_list = [str(year) for year in range(present_year-100,present_year+1)]
        # selected_year = st.selectbox("Select Year",options=year_list,index=len(year_list)-1)
        # scores = get_scores(datetime.date(int(selected_year), 1, 1), datetime.date(int(selected_year), 12, 31))
        # heat_map = july.heatmap(scores.keys(), scores.values(), title='Sentiment Map', cmap="github")
        # st.pyplot(heat_map.figure)
        # st.table(pd.DataFrame(character_info))
