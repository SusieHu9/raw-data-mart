import requests
import json
import pandas as pd
import streamlit as st
url = 'https://raw-data-mart-default-rtdb.firebaseio.com/'
st.set_page_config(page_title="“Will Call” Raw Data Mart", page_icon=":floppy_disk:", layout="wide")
st.title('Authority Management')

if not 'info_user' in st.session_state:
    st.header('💁 Your session has expired.')
    st.write('Your session ended. Please sign in again.')
    st.image('https://cdn.dribbble.com/users/1150186/screenshots/6290394/session_timeout_warning.jpg',width=400)
else:    
    if (st.session_state['info_user']['permission'][4] == '0'):
        st.header('💁 Forbidden')
        st.write('You don\'t have permission to access this resource. Please ask for permission to access.')
        import random
        random_number = random.randint(0, 2)
        urls = ['https://http.dog/403.jpg','https://httpcats.com/403.jpg','https://http.garden/403.jpg']
        st.image(urls[random_number],width=400)
    else:   
        if not "group" in st.session_state:
            st.session_state["group"] = None
        if not "role" in st.session_state:
            st.session_state["role"] = ''
        if not "flag" in st.session_state:
            st.session_state["flag"] = ''
        
        if st.session_state["flag"] == 1:
            st.success('Action Successful')
            st.session_state.role = ''
            st.session_state["flag"] = ''
        
        
        # function
        def random_invitation():
            import random
            import string
            length = 10
            num_digits = 5
            num_chars = length - num_digits   
            code_chars = []
            for i in range(num_digits):
                code_chars.append(random.choice(string.digits))
            for i in range(num_chars):
                code_chars.append(random.choice(string.ascii_letters))
            random.shuffle(code_chars)
            invitation_code = ''.join(code_chars)
            return invitation_code
        
        def send_email(name, receiver_email,invitation_code):
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Set up the email parameters
            sender_email = "***@gmail.com"
            receiver_email = receiver_email
            password = "***"
            subject = "Invitation from Raw Data Mart"
            
            # Create a message object
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject
            
            # Add the body text to the message object
            body = "Dear " + name + ", \n\nWe sincerely invite you to join Raw Data Mart! Your invitation code is: \n\n"+ invitation_code +"\n\nPlease enter the above invitation code when you register your account. Thank you!\n\nBest Regards,\n\nRaw Data Mart Team"
            message.attach(MIMEText(body, "plain"))
            
            # Create a SMTP session
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            
            # Log in to the email account
            server.login(sender_email, password)
            
            # Send the email
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
            
            # Close the SMTP session
            server.quit()
            
            return invitation_code
        
        def validate_email(email):
            import re
            # A regular expression pattern to match valid email addresses
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            # Match the pattern against the email address using regex
            if re.match(pattern, email):
                return True
            else:
                return False
            
        st.header('Current User Table')
        
        def aggrid_interactive_table(df: pd.DataFrame):
            from st_aggrid import AgGrid, GridOptionsBuilder
            from st_aggrid.shared import GridUpdateMode
        
            options = GridOptionsBuilder.from_dataframe(
                df, enableRowGroup=True, enableValue=True, enablePivot=True
            )
        
            options.configure_side_bar()
        
            options.configure_selection("single")
            selection = AgGrid(
                df,
                fit_columns_on_grid_load = True,
                enable_enterprise_modules=True,
                gridOptions=options.build(),
                update_mode=GridUpdateMode.MODEL_CHANGED,
                allow_unsafe_jscode=True,
            )
        
            return selection
            
        df = pd.DataFrame(json.loads(requests.get(url+'user.json').text).values())
        df['status'] = df['password'].apply(lambda x: 'inactive' if pd.isna(x) else 'active')
        
        
        selection = aggrid_interactive_table(df=df[['name','email','group','role','invitecode','status']])
            
        tab1, tab2, tab3, tab4 = st.tabs(["Add User", "Remove User", "Modify Authority","Setting"])
        
        with tab1:
            st.selectbox('Role:',('','admin','coach','participant','researcher'), key = 'role')
            permission_default = {'admin':'11111','researcher':'11110','coach':'10010','participant':'00010'}
            if st.session_state["role"] == 'admin':
                with st.form('Send Email_admin'):
                    name = st.text_input("Name:")
                    email = st.text_input("Email:")
                    st.multiselect('Group:',['admin'],['admin'], key = 'group')
                    st.markdown("""
                    <style>
                    .title_sheet {
                        font-size:14px;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.markdown('<p class="title_sheet">Authority:</p>', unsafe_allow_html=True)
                    col3, col4, col5, col6, col7 = st.columns(5)
                    with col3:
                        upload = st.checkbox('Upload',permission_default['admin'][0])
                    with col4:
                        delete = st.checkbox('Delete',permission_default['admin'][1])
                    with col5:
                        modify = st.checkbox('Modify',permission_default['admin'][2])
                    with col6:
                        retrieve = st.checkbox('Retrieve',permission_default['admin'][3])
                    with col7:
                        auth_manage = st.checkbox('Manage',permission_default['admin'][4])
                    st.write("")
                    submitted2 = st.form_submit_button("Send Email For Invitation")
                    if submitted2:
                        if (name != "") & (validate_email(email)):
                            invitecode = random_invitation()
                            import datetime
                            import uuid
                            userid = str(uuid.uuid4())[:8]
                            a = requests.patch(url+'user/'+ userid +'.json', 
                                           json = {"name":name,
                                                   "email": email,
                                                   "group": st.session_state["group"],
                                                   "invitecode": invitecode,
                                                   "invitetime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                   "permission": str(int(upload))+str(int(delete))+str(int(modify))+str(int(retrieve))+str(int(auth_manage)),
                                                   "role": st.session_state["role"],
                                                   "userid": userid
                                                   })
                            send_email(name = name, receiver_email =email, invitation_code = invitecode)
                            st.session_state["flag"] = 1
                            st.experimental_rerun()     
                        else:
                            st.error('Error: Fail to send email')
                    
            elif (st.session_state["role"] == 'participant') or (st.session_state["role"] == 'coach') or (st.session_state["role"] == 'researcher'):
                with st.form('Send Email_admin'):
                    name = st.text_input("Name:")
                    email = st.text_input("Email:")
                    group_list = json.loads(requests.get(url+'setting/group.json').text)
                    group_list.remove('admin')
                    st.multiselect(label = 'Group', options = group_list,default = None, key ='group')
                    st.markdown("""
                    <style>
                    .title_sheet {
                        font-size:14px;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.markdown('<p class="title_sheet">Authority:</p>', unsafe_allow_html=True)
                    col3, col4, col5, col6, col7 = st.columns(5)
                    if st.session_state["role"] != "":
                        with col3:
                            upload = st.checkbox('Upload',int(permission_default[st.session_state["role"]][0]))
                        with col4:
                            delete = st.checkbox('Delete',int(permission_default[st.session_state["role"]][1]))
                        with col5:
                            modify = st.checkbox('Modify',int(permission_default[st.session_state["role"]][2]))
                        with col6:
                            retrieve = st.checkbox('Retrieve',int(permission_default[st.session_state["role"]][3]))
                        with col7:
                            auth_manage = st.checkbox('Manage',int(permission_default[st.session_state["role"]][4]))
                    else:
                        with col3:
                            upload = st.checkbox('Upload')
                        with col4:
                            delete = st.checkbox('Delete')
                        with col5:
                            modify = st.checkbox('Modify')
                        with col6:
                            retrieve = st.checkbox('Retrieve')
                        with col7:
                            auth_manage = st.checkbox('Manage')
                    st.write("")
                    submitted2 = st.form_submit_button("Send Email For Invitation")
                    if submitted2:
                        if (name != "") & (validate_email(email)):
                            invitecode = random_invitation()
                            import datetime
                            import uuid
                            userid = str(uuid.uuid4())[:8]
                            a = requests.patch(url+'user/'+ userid +'.json', 
                                           json = {"name":name,
                                                   "email": email,
                                                   "group": st.session_state["group"],
                                                   "invitecode": invitecode,
                                                   "invitetime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                   "permission": str(int(upload))+str(int(delete))+str(int(modify))+str(int(retrieve))+str(int(auth_manage)),
                                                   "role": st.session_state["role"],
                                                   "userid": userid
                                                   })
                            send_email(name = name, receiver_email =email, invitation_code = invitecode)
                            st.session_state["flag"] = 1
                            st.experimental_rerun()     
                        else:
                            st.error('Error: Fail to send email')
        with tab2:
            if selection.selected_rows != []:
                st.write("You selected:")
                status_select = pd.DataFrame(selection["selected_rows"])['status'][0]
                email_select = pd.DataFrame(selection["selected_rows"])['email'][0]
                info_select = dict(list(json.loads(requests.get(url+'user.json?orderBy="email"&equalTo="'+email_select+'"').text).values())[0])
                info_select['status'] = status_select
                st.write(pd.DataFrame.from_dict(info_select,orient='index',columns = ['info']))
                
                deleted = st.button('Remove the selected user')
                if deleted:
                    a = requests.delete(url+'user/{}.json'.format(info_select['userid']))
                    if a.status_code == 200:
                        st.session_state["flag"] = 1
                        st.experimental_rerun()
                    else:
                        st.error('Error: Fail to remove the selected user')
                        
            else:
                st.write("Please select a user to delete first.")
        
        with tab3:
            if selection.selected_rows != []:
                st.write("Current information:")
                email_select = pd.DataFrame(selection["selected_rows"])['email'][0]
                info_select = dict(list(json.loads(requests.get(url+'user.json?orderBy="email"&equalTo="'+email_select+'"').text).values())[0])
                with st.form('Modify Authority'):
                    name = st.text_input(label = "Name:", value = info_select['name'], disabled = True)
                    email = st.text_input(label = "Email:", value = info_select['email'], disabled = True)
                    list_role = [info_select['role']]
                    for x in ['admin','coach','participant','researcher']:
                        if x != info_select['role']:
                            list_role.append(x)
                    if info_select['role'] == 'admin':
                        role = st.selectbox("Role:", list_role,disabled=True)
                        st.multiselect(label = 'Group', options = ['admin'],default = info_select['group'], key ='group1',disabled=True)
                    else:
                        role = st.selectbox("Role:", list_role)
                        group_list1 = json.loads(requests.get(url+'setting/group.json').text)
                        group_list1.remove('admin')
                        st.multiselect(label = 'Group', options = group_list1,default = info_select['group'], key ='group1')
                    st.markdown("""
                    <style>
                    .title_sheet {
                        font-size:14px;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.markdown('<p class="title_sheet">Authority:</p>', unsafe_allow_html=True)
                    col3, col4, col5, col6, col7 = st.columns(5)
                    with col3:
                        upload = st.checkbox('Upload',int(info_select['permission'][0]))
                    with col4:
                        delete = st.checkbox('Delete',int(info_select['permission'][1]))
                    with col5:
                        modify = st.checkbox('Modify',int(info_select['permission'][2]))
                    with col6:
                        retrieve = st.checkbox('Retrieve',int(info_select['permission'][3]))
                    with col7:
                        auth_manage = st.checkbox('Manage',int(info_select['permission'][4]))
                    st.write("")
                    modified = st.form_submit_button('Save the changes')   
                if modified:
                    a = requests.patch(url+'user/'+ info_select['userid'] +'.json', 
                                   json = {"group": st.session_state["group1"],
                                           "permission": str(int(upload))+str(int(delete))+str(int(modify))+str(int(retrieve))+str(int(auth_manage)),
                                           "role": role,
                                           })
                    if a.status_code == 200:
                        st.session_state["flag"] = 1
                        st.experimental_rerun()
                    else:
                        st.error('Error: Fail to save the changes')
            else:
                st.write("Please select a user to modify first.")
        
        with tab4:
            group_list2 = json.loads(requests.get(url+'setting/group.json').text)
            st.multiselect(label = 'Current Groups:', options = group_list2, default = group_list2, disabled= True)
            option = st.radio("Add or Remove Group?", ("Add", "Remove"))
            if option == "Add":
                add_group = st.text_input(label='New Group:')
                added = st.button('Add a new group')
                if added:
                    group_list2.append(add_group)
                    a = requests.put(url+'/setting/group.json',json = group_list2)
                    if a.status_code == 200:
                        st.session_state["flag"] = 1
                        st.experimental_rerun()
                    else:
                        st.error('Error: Fail to add the group')                
            elif option == "Remove":
                group_list2.insert(0,"")
                remove_group = st.selectbox('Current Groups:',group_list2)
                removed = st.button('Remove a group')
                if removed:
                    group_list2.remove(remove_group)
                    group_list2.remove("")
                    a = requests.put(url+'/setting/group.json',json = group_list2)
                    if a.status_code == 200:
                        st.session_state["flag"] = 1
                        st.experimental_rerun()
                    else:
                        st.error('Error: Fail to remove the group')       
            
                
            
            
            
            
            
            
    
    
    
                            
                            
                        
    
                            
                    
                    
            
        
            
    
       
        
    
