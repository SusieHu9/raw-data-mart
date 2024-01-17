import streamlit as st
import requests
import json
import pandas as pd
url = 'https://raw-data-mart-default-rtdb.firebaseio.com/'


st.set_page_config(page_title="“Will Call” Raw Data Mart", page_icon=":floppy_disk:", layout="wide")
st.title('Upload File')

if not 'info_user' in st.session_state:
    st.header('💁 Your session has expired.')
    st.write('Your session ended. Please sign in again.')
    st.image('https://cdn.dribbble.com/users/1150186/screenshots/6290394/session_timeout_warning.jpg',width=400)
else:
    if (st.session_state['info_user']['permission'][0] == '0'):
        st.header('💁 Forbidden')
        st.write('You don\'t have permission to access this resource. Please ask for permission to access.')
        import random
        random_number = random.randint(0, 2)
        urls = ['https://http.dog/403.jpg','https://httpcats.com/403.jpg','https://http.garden/403.jpg']
        st.image(urls[random_number],width=400)
    else:
        
        # st.session_state
        if not "create" in st.session_state:
            st.session_state['create'] = None
        if not "new_tag" in st.session_state:
            st.session_state['new_tag'] = dict()
        if not "new_tag_update" in st.session_state:
            st.session_state['new_tag_update'] = dict()
        if not "new_data" in st.session_state:
            st.session_state['new_data'] = dict()
        if not "new_data_update" in st.session_state:
            st.session_state['new_data_update'] = dict()
        if not "new_video" in st.session_state:
            st.session_state['new_video'] = dict()
        if not "new_video_update" in st.session_state:
            st.session_state['new_video_update'] = dict()
        if not "new_pic" in st.session_state:
            st.session_state['new_pic'] = dict()
        if not "new_pic_update" in st.session_state:
            st.session_state['new_pic_update'] = dict()
        if not "participantid" in st.session_state:
            st.session_state['participantid'] = 0
        if not "collectionid" in st.session_state:
            st.session_state['collectionid'] = ''
        
        js = '''
        <script>
            var body = window.parent.document.querySelector(".main");
            console.log(body);
            body.scrollTop = 0;
        </script>
        '''
        
        
        st.subheader('Pariticipant Information:')
        add = st.radio("Create or Find a participant?", ("Create", "Find"))
        if add == 'Create':
            st.session_state['create'] = 1 
            col1, col2 = st.columns(2)
            with col1:
                participant = st.text_input('Name:')
                sex = st.radio('Sex:',('male','female','other'),horizontal=True)
            with col2:
                if st.session_state['participantid'] == 0:
                    participantid = json.loads(requests.get(url + 'setting/object/participantid.json').text) + 1
                    st.session_state['participantid'] = participantid
                else:
                    participantid = st.session_state['participantid']
                st.text_input('Participant ID:',participantid, disabled=True)
                birthdate = st.date_input('Birth Date:', value=None)
            col1, col2, col3, col4, col5 = st.columns([1,1,1,1,4])
            with col1:
                height1= st.text_input('Height:')
            with col2:
                st.write("#")
                st.write("feet")
            with col3:
                height2 = st.text_input('Height1:',label_visibility="hidden")
            with col4:
                st.write("#")
                st.write("inches")
            with col5:
                weight = st.text_input('Weight(lbs):')
          
        elif add == 'Find':
            with st.form('Find a participant'):
                from datetime import datetime
                participant = st.text_input('Name:')
                birthdate = st.date_input('Birth Date:', value=None, min_value=datetime.strptime('1900/01/01', "%Y/%m/%d"))
                find = st.form_submit_button('Find')
            if find:
                st.session_state['create'] = 0
        
        
        if (st.session_state['create'] == 0):
            birthdate = birthdate.strftime("%Y-%m-%d")
            a = json.loads(requests.get(url+'setting/object.json?orderBy="name"&equalTo="'+
                         participant+'"').text)
            if a=={}:
                st.error('We can not find a current participant match')
            elif list(a.values())[0]['birthdate'] != birthdate:
                st.error('We can not find a current participant match')
            else:
                sex = list(a.values())[0]['sex']
                participantid = list(a.keys())[0]
                st.session_state['participantid'] = participantid
                st.write('We find the participant. Participant ID is',participantid,'.')
                col1, col2, col3, col4, col5 = st.columns([1,1,1,1,4])
                with col1:
                    height1= st.text_input('Height:')
                with col2:
                    st.write("#")
                    st.write("feet")
                with col3:
                    height2 = st.text_input('Height1:',label_visibility="hidden")
                with col4:
                    st.write("#")
                    st.write("inches")
                with col5:
                    weight = st.text_input('Weight(lbs):')
        
        st.write("")
        
        try:
            if (participant!='') and (st.session_state['collectionid'] == ''):
                settingObj = json.loads(requests.get(url+"setting/object/"+str(participantid)+".json").text)
        
                if settingObj is not None: # add new collection
                    collectionid = settingObj['collectionid'] + 1
                    settingObj['collectionid'] = collectionid
                    requests.put(url+"setting/object/"+str(participantid)+".json",json=settingObj)
                    st.session_state['collectionid'] = collectionid
        except:
            print()
                
        st.subheader('Collection Information:')
        
        group_list = json.loads(requests.get(url+"setting/group.json").text)
        group_list.remove('admin')
        group_list.append('public')
        group = st.multiselect("Group",group_list,[])
        
        collectiontype = st.text_input("Collection Type")
        date = st.date_input("Collection Date")
        
        # new tags
        st.write()        
        
        if st.session_state['new_tag_update'] != dict():
            for k,v in st.session_state['new_tag_update'].items():
                st.text_input(k,v)
        if st.session_state['new_tag_update'] == dict():
            option_tags = st.radio('Add New Tags:',(range(0,11,1)),horizontal=True,key= "option_tag" )
        else:
            option_tags = 0
            
        def add_new_row(i):
            import random, string
            col1, col2 = st.columns(2)
            with col1:
                k = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
                st.text_input('Tag{} Name:'.format(i+1),key= k)
            with col2:
                v = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
                st.text_input('Tag{} Value:'.format(i+1),key= v)
            return k,v
        
        def catch_collection_id():
            settingObj = json.loads(requests.get(url+"setting/object/"+str(participantid)+".json").text)
        
            if (settingObj is not None) and (st.session_state['collectionid'] == ''): # add new collection
                collectionid = settingObj['collectionid'] + 1
                settingObj['collectionid'] = collectionid
                requests.put(url+"setting/object/"+str(participantid)+".json",json=settingObj)
                st.session_state['collectionid'] = collectionid
        
            elif (settingObj is None): # create
                newObject = dict()
                collectionid = participantid * 1000 + 1
                newObject = {
                    'birthdate': str(birthdate),
                    'collectionid': collectionid,
                    'name': participant,
                    'sex': sex
                }
                if participant != '':
                    requests.put(url+"setting/object/"+str(participantid)+".json",json=newObject)
                    requests.put(url+"setting/object/participantid.json",json=participantid)
                    st.session_state['collectionid'] = collectionid
                    st.session_state['participantid'] = participantid
                
        if (option_tags != 0):
            new_tag = dict()
            with st.form('new_tags'):
                for i in range(0,option_tags):
                    k,v = add_new_row(i)
                    new_tag[k]=v
                st.session_state['new_tag'] = new_tag
                def change_new_tag():
                    new_tag1 = st.session_state['new_tag'].copy()
                    new_tag = st.session_state['new_tag_update']
                    for i in range(0,len(list(new_tag1.items()))):
                        new_tag[st.session_state[list(new_tag1.items())[i][0]]]=st.session_state[list(new_tag1.items())[i][1]]
                    st.session_state['new_tag_update'] = new_tag
                    catch_collection_id()
                    
                save = st.form_submit_button('Save', on_click=change_new_tag)
                
        
            
        # new data
        st.write("")
        st.subheader('Upload Force data:')
        
        option_data = st.radio('Add Data',(range(0,11,1)),horizontal=True)
        
        def add_new_data(i):
            import random, string
            des = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
            st.text_input('Data{} Description'.format(i+1),key = des)
            data = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
            st.file_uploader("Choose csv or xlsx file for file{}".format(i+1),type = ['csv','xlsx'], accept_multiple_files=False,key =data)
            return des,data
        
        
        def upload_data(file, i, key):
            df = pd.read_csv(file)
            df = df.to_dict()
            
            dk = len(json.loads(requests.get(url+'data.json').text))
            requests.put(url+'data/'+ str(dk) +'.json',json = df)
            
            data = dict()
            data['collectionid'] = str(st.session_state['collectionid'])
            data['participant'] = participant
            data['participantid'] = participantid
            data['sex'] = sex
            data['birthdate'] = str(birthdate)
            data['height'] = height1 + '\'' + height2 + '"'
            data['weight'] = weight
            data['group'] = group
            data['collectiontype'] = collectiontype
            if st.session_state['new_tag_update'] != dict():
                for k in st.session_state['new_tag_update']:
                    data[k] = st.session_state['new_tag_update'][k]
            data['description'] = key
            data['location'] = 'data/' + str(dk) +'.json'
            from datetime import datetime
            data['created'] = str(datetime.now())[:10]
            data['datatype'] = 'Force'
            data['date'] = str(date)
            data['modified'] = str(datetime.now())[:19]
            data['objectname'] = participant + ' ' +collectiontype+ ' Force ' + str(datetime.now())[:10] + ' #' +key
            data['user_access'] = [{'action':'create','success':1,'time':str(datetime.now())[:19],'username':st.session_state['info_user']['name']}]
            kk = len(json.loads(requests.get(url+'object.json').text))
            requests.put(url+'object/'+str(kk)+'.json',json = dict(data))
            st.success('Force Data {} Successfully Uploaded'.format(i+1))
            
        
        def change_new_data():
            new_data1 = st.session_state['new_data'].copy()
            new_data = st.session_state['new_data_update']
            for i in range(0,len(list(new_data1.items()))):
                key = st.session_state[list(new_data1.items())[i][0]]
                new_data[st.session_state[list(new_data1.items())[i][0]]]=st.session_state[list(new_data1.items())[i][1]]
                file = st.session_state[list(new_data1.items())[i][1]]
                if file is not None:
                    with st.spinner('Uploading...'):
                        st.components.v1.html(js)
                        upload_data(file, i, key)
            st.session_state['new_data_update'] = new_data
            
        
        if option_data != 0:
            new_data = dict()
            with st.form('new_dataa'):
                for i in range(0,option_data):
                    k,v = add_new_data(i)
                    new_data[k]=v
                st.session_state['new_data'] = new_data
                save = st.form_submit_button('Save', on_click=change_new_data)               
              
                    
                    
                    
        
        # new video
        import boto3
        AWS_ACCESS_KEY_ID = '*****'
        AWS_SECRET_ACCESS_KEY = '*****'
        BUCKET_NAME = 'rawdatamart'
        st.write("")
        st.subheader("Upload Videos:")
        
        option_video = st.radio('Add Video',(range(0,11,1)),horizontal=True)
        
        def add_new_video(i):
            import random, string
            des = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
            st.text_input('Video{} Description'.format(i+1),key = des)
            video = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
            st.file_uploader("Choose mp4 or mov file for file{}".format(i+1),type = ['mov','mp4'], accept_multiple_files=False,key =video)
            return des,video
        def upload_video(file, i, key):
            import os.path
            with open(os.path.join("tempDir",file.name),"wb") as f: 
              f.write(file.getbuffer())
            s3_client = boto3.client('s3',
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            video_name = file.name
        
            try:
                objectKey = str(participantid) + '/' + str(st.session_state['collectionid']) +'/'+video_name
                file_name = './tempDir/' + file.name
                s3_client.upload_file(file_name,
                                Bucket=BUCKET_NAME,
                                Key=objectKey,
                                ExtraArgs={'ACL': 'public-read'}
                                )
                st.success('Video {} Successfully Uploaded'.format(i+1))
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=objectKey)
                if response is not None and response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    objectUrl = f"https://{BUCKET_NAME}.s3.amazonaws.com/{objectKey}"
                    st.session_state['new_video_update'][key] = objectUrl
                
                
                data = dict()
                data['collectionid'] = str(st.session_state['collectionid'])
                data['participant'] = participant
                data['participantid'] = participantid
                data['sex'] = sex
                data['birthdate'] = str(birthdate)
                data['height'] = height1 + '\'' + height2 + '"'
                data['weight'] = weight
                data['group'] = group
                data['collectiontype'] = collectiontype
                if st.session_state['new_tag_update'] != dict():
                    for k in st.session_state['new_tag_update']:
                        data[k] = st.session_state['new_tag_update'][k]
                data['description'] = key
                data['location'] = objectUrl 
                from datetime import datetime
                data['created'] = str(datetime.now())[:10]
                data['datatype'] = 'Video'
                data['date'] = str(date)
                data['modified'] = str(datetime.now())[:19]
                data['objectname'] = participant + ' ' +collectiontype+ ' Video ' + str(datetime.now())[:10] + ' #' +key
                data['user_access'] = [{'action':'create','success':1,'time':str(datetime.now())[:19],'username':st.session_state['info_user']['name']}]
                kk = len(json.loads(requests.get(url+'object.json').text))
                requests.put(url+'object/'+str(kk)+'.json',json = dict(data))
        
        
                return True
            except FileNotFoundError:
                st.error('There is an error whiling uploading, please try agian. ')
                return False
        
        def change_new_video():
            new_video1 = st.session_state['new_video'].copy()
            new_video = st.session_state['new_video_update']
            for i in range(0,len(list(new_video1.items()))):
                key = st.session_state[list(new_video1.items())[i][0]]
                new_video[st.session_state[list(new_video1.items())[i][0]]]=st.session_state[list(new_video1.items())[i][1]]
                file = st.session_state[list(new_video1.items())[i][1]]
                if file is not None:
                    with st.spinner('Uploading...'):
                        st.components.v1.html(js)
                        upload_video(file, i, key)
            st.session_state['new_video_update'] = new_video
        
        
        if option_video != 0:
            new_video = dict()
            with st.form('new_videos'):
                for i in range(0,option_video):
                    k,v = add_new_video(i)
                    new_video[k]=v
                st.session_state['new_video'] = new_video #here
                save = st.form_submit_button('Save', on_click=change_new_video)
        
                
        
        # new picture
        st.write("")
        st.subheader("Upload Images:")
        
        option_pic = st.radio('Add Pictures',(range(0,11,1)),horizontal=True)
        
        def add_new_pic(i):
            import random, string
            des = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
            st.text_input('Picture{} Description'.format(i+1),key = des)
            pic = random.choice(string.ascii_uppercase)+str(random.randint(0,999999))
            st.file_uploader("Choose a jpg/png/jpeg file for file{}".format(i+1),type = ['jpg','png','jpeg'], accept_multiple_files=False,key =pic)
            new_pic[des] = pic
            return des, pic
        
        if option_pic != 0:
            new_pic = dict()
            with st.form('new_pics'):
                for i in range(0,option_pic):
                    k,v = add_new_pic(i)
                    new_pic[k]=v
                st.session_state['new_pic'] = new_pic
        
                def upload_pic(file, i, key):
                    import os.path
                    with open(os.path.join("tempDir",file.name),"wb") as f: 
                        f.write(file.getbuffer())
                    s3_client = boto3.client('s3',
                                 aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                    pic_name = file.name
        
                    try:
                        objectKey = str(participantid) + '/' + str(st.session_state['collectionid']) +'/'+pic_name
                        file_name = './tempDir/' + file.name
                        s3_client.upload_file(file_name,
                                        Bucket=BUCKET_NAME,
                                        Key=objectKey,
                                        ExtraArgs={'ACL': 'public-read'}
                                        )
                        st.success('Image{} Successfully Uploaded'.format(i+1))
                        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=objectKey)
                        if response is not None and response['ResponseMetadata']['HTTPStatusCode'] == 200:
                            objectUrl = f"https://{BUCKET_NAME}.s3.amazonaws.com/{objectKey}"
                            st.session_state['new_pic_update'][key] = objectUrl
                        
                        
                        data = dict()
                        data['collectionid'] = str(st.session_state['collectionid'])
                        data['participant'] = participant
                        data['participantid'] = participantid
                        data['sex'] = sex
                        data['birthdate'] = str(birthdate)
                        data['height'] = height1 + '\'' + height2 + '"'
                        data['weight'] = weight
                        data['group'] = group
                        data['collectiontype'] = collectiontype
                        if st.session_state['new_tag_update'] != dict():
                            for k in st.session_state['new_tag_update']:
                                data[k] = st.session_state['new_tag_update'][k]
                        data['description'] = key
                        data['location'] = objectUrl 
                        from datetime import datetime
                        data['created'] = str(datetime.now())[:10]
                        data['datatype'] = 'Image'
                        data['date'] = str(date)
                        data['modified'] = str(datetime.now())[:19]
                        data['objectname'] = participant + ' ' +collectiontype+ ' Image ' + str(datetime.now())[:10] + ' #' +key
                        data['user_access'] = [{'action':'create','success':1,'time':str(datetime.now())[:19],'username':st.session_state['info_user']['name']}]
                        kk = len(json.loads(requests.get(url+'object.json').text))
                        requests.put(url+'object/'+str(kk)+'.json',json = dict(data))
                        
                        
                        
                        
                        return True
                    except FileNotFoundError:
                        st.error('There is an error whiling uploading, please try agian. ')
                        return False
                def change_new_pic():
                    new_pic1 = st.session_state['new_pic'].copy()
                    new_pic = st.session_state['new_pic_update']
                    for i in range(0,len(list(new_pic1.items()))):
                        key = st.session_state[list(new_pic1.items())[i][0]]
                        new_pic[st.session_state[list(new_pic1.items())[i][0]]]=st.session_state[list(new_pic1.items())[i][1]]
                        file = st.session_state[list(new_pic1.items())[i][1]]
                        if file is not None:
                            with st.spinner('Uploading...'):
                                st.components.v1.html(js)
                                upload_pic(file, i, key)
                    st.session_state['new_pic_update'] = new_pic
                    
                save = st.form_submit_button('Save', on_click=change_new_pic)
            
        
        finish = st.button('Finish this collection')
        if finish:
            for k in st.session_state.keys():
                if (k == str('info_user')) or (k == str('status')):
                    print()
                else:
                    del st.session_state[k]
            st.experimental_rerun()
            
