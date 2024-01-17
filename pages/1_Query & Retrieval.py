import streamlit as st
import requests
import json
import pandas as pd
url = 'https://raw-data-mart-default-rtdb.firebaseio.com/'
st.set_page_config(page_title="“Will Call” Raw Data Mart", page_icon=":floppy_disk:", layout="wide")
st.title('Query and Retrieval')

if not 'info_user' in st.session_state:
    st.header('💁 Your session has expired.')
    st.write('Your session ended. Please sign in again.')
    st.image('https://cdn.dribbble.com/users/1150186/screenshots/6290394/session_timeout_warning.jpg',width=400)
else:
    if (st.session_state['info_user']['permission'][3] == '0'):
        st.header('💁 Forbidden')
        st.write('You don\'t have permission to access this resource. Please ask for permission to access.')
        import random
        random_number = random.randint(0, 2)
        urls = ['https://http.dog/403.jpg','https://httpcats.com/403.jpg','https://http.garden/403.jpg']
        st.image(urls[random_number],width=400)
    else:
        a = []
        a_ori = json.loads(requests.get(url+'object.json?orderBy="delete"&endAt=0').text)
        for a_i in a_ori.values():
            if (set(st.session_state['info_user']['group']) >= set(a_i['group'])) or ('admin' in st.session_state['info_user']['group']) or ('public' in set(a_i['group'])):
                a.append(a_i)
        print(a)
        b = json.loads(requests.get(url+'setting/object.json').text)
        if 'admin' in st.session_state['info_user']['group']:
            c = json.loads(requests.get(url+'setting/group.json').text)
            c.remove('admin')
            c.insert(0,'public')
        else:
            c = st.session_state['info_user']['group'].copy()
            c.insert(0,'public')
        col1, col2, col3 = st.columns(3,gap="small")
        with col1:
            b1 = list(b.keys())
            b1.remove('participantid')
            b1.insert(0,'')
            participantid = st.selectbox('Participant ID',b1)
            collectionid = st.text_input('Collection ID')
            b2 = ['Image', 'Video', 'Force']
            b2.insert(0,'')
            datatype = st.selectbox('Data Type', b2)
        with col2:
            participantname = st.text_input('Participant Name')
            collectdate = st.text_input('Collect Date',placeholder='YYYY-MM-DD')
            createdate = st.text_input('Created Date',placeholder='YYYY-MM-DD')
        with col3:
            group = st.multiselect('Group',c)
            
            collectiontype = st.text_input('Collection Type')
            modifydate = st.text_input('Modified Date',placeholder='YYYY/MM/DD')
        
        if ("customize" in st.session_state) and (len(st.session_state['customize']) != 0):
            col1, col2, col3 = st.columns(3,gap="small")
            with col1:
                for i in range(0,len(st.session_state['customize']),3):
                    st.text_input(st.session_state['customize'][i], key = st.session_state['customize'][i])
            with col2:
                for i in range(1,len(st.session_state['customize']),3):
                    st.text_input(st.session_state['customize'][i], key = st.session_state['customize'][i])
            with col3:
                for i in range(2,len(st.session_state['customize']),3):
                    st.text_input(st.session_state['customize'][i], key = st.session_state['customize'][i])
        
        
        tag_list = []
        for i in a:
            tag_list = tag_list + list(i.keys())
        tag_list = set(tag_list)
        remove_list = ['collectionid','collectiontype','created','datatype','date','group','objectname','modified','participant','participantid','location','modified', 'user_access']
        res = [i for i in tag_list if i not in remove_list]
        st.multiselect('Customized Tags Name',res,key = "customize")
        
        
        find = {}
        find['participantid'] = participantid
        find['participant'] = participantname
        find['group'] = group
        find['collectionid'] = collectionid
        find['date'] = collectdate
        find['collectiontype'] = collectiontype
        find['datatype'] = datatype
        find['created'] = createdate
        find['modified'] = modifydate
        
        find1 = find.copy()
        
        for i in st.session_state['customize']:
            if (i in st.session_state) and (st.session_state[i]!=''):
                find[i] = st.session_state[i]
        
        emptyK = []
        for k,v in find.items():
            if v == '' or len(v) == 0:
                emptyK.append(k)
        for k in emptyK:
            find.pop(k)
        
        
        find_result = a.copy()
        
        for k,v in find.items():
            if k=='collectiontype':
                find_result = list(filter(lambda d: k in d, find_result))
                find_result = list(filter(lambda d: d[k].lower() == v.lower(), find_result))
            elif k=='group':
                # find_result = list(filter(lambda d: k in d, find_result))
                find_result = list(filter(lambda d: set(v) <= set(d[k]), find_result))
                #for group in v:
                    #find_result = list(filter(lambda d: group in d[k], find_result))
                
            elif k=='modified':
                find_result = list(filter(lambda d: k in d, find_result))
                find_result = list(filter(lambda d: d[k].split(' ')[0] == v, find_result))
            elif k=='description':
                find_result = list(filter(lambda d: k in d, find_result))
                for word in v.lower().split(' '):
                    find_result = list(filter(lambda d: word in d[k].lower().split(' '), find_result))
            elif k == 'participantid':
                find_result = list(filter(lambda d: k in d, find_result))
                find_result = list(filter(lambda d: str(d[k]) == v, find_result))
            else:
                find_result = list(filter(lambda d: k in d, find_result))
                find_result = list(filter(lambda d: d[k] == v, find_result))
        
        
        for aa in find_result :
            aa['user_access'] = ''     
            aa['participantid'] = str(aa['participantid'])
        
        st.title('Here are query results:')
        
        if find_result != []:
            show_list = ['objectname']+[key for key in list(find1.keys())]
            df = pd.DataFrame(find_result)[show_list]
            
            import numpy as np
            d = pd.DataFrame.from_dict({'download':list(np.repeat(False,len(find_result),axis=0)),
            'preview':list(np.repeat(False,len(find_result),axis=0))})
            df.reset_index()
            d.reset_index()
            df = pd.concat([d,df], axis = 1)
            
            df_new = st.experimental_data_editor(df)
            
            if True in list(df_new['download']):
                downloaded = st.button('download selected')
                if downloaded:
                    import youtube_dl
                    import os
                    import zipfile
                    
                    def download_and_rename_videos(url_list_force, url_list_video, url_list_image, name_list_force,
                                               name_list_video,name_list_image, select_df,placeholder, my_bar,progress_text):
                        download_dir = './tempDir/download/'
                        new_name_list = []
                        # data
                        
                        for i, url_i in enumerate(url_list_force):
                            df1 = pd.DataFrame(json.loads(requests.get(url + url_i).text))
                            df1.to_csv(download_dir+name_list_force[i]+'.csv', index=False)
                            new_name_list.append(name_list_force[i]+'.csv')
                        my_bar.progress(10, text=progress_text)
                        # video
                        ydl_opts = {'outtmpl': download_dir + '%(title)s.%(ext)s',}
                        ydl = youtube_dl.YoutubeDL(ydl_opts)
                      
                        # iterate through the list of URLs and download the videos
                        for i, url_i in enumerate(url_list_video):
                            # get the video title
                            video_info = ydl.extract_info(url_i, download=False)
                            video_title = video_info['title']
                            extension = video_info['ext']
                            # set the new name for the video
                            new_name = name_list_video[i]
                            
                            # download the video
                            ydl.download([url_i])
                            
                            # rename the video
                            os.rename('./tempDir/download/'+video_title+'.'+extension,'./tempDir/download/'+new_name+'.'+extension)
                            new_name_list.append(new_name+'.'+extension)
                        my_bar.progress(80, text=progress_text)
                        # image
                        for i, url_i in enumerate(url_list_image):
                            response = requests.get(url_i)
                            extension = url_i.split('.')[-1]
                            new_name = name_list_image[i].split('.')[0] + '.' + extension
                            with open(os.path.join(download_dir, new_name), 'wb') as f:
                                f.write(response.content)
                            new_name_list.append(new_name)
                        my_bar.progress(90, text=progress_text)
                        # metadata
                        from datetime import datetime
                        now_time = str(datetime.now())[:19]
                        metadata_name = 'metadata-'+now_time+'.csv'
                        select_df.to_csv(download_dir+metadata_name, index=False)
                        new_name_list.append(metadata_name)
                        my_bar.progress(95, text=progress_text)
                        
                        # create a zip file of the downloaded and renamed videos
                        with zipfile.ZipFile('../download-result-'+now_time+'.zip', 'w') as zip:
                            for new_name in list(new_name_list):
                                zip.write('tempDir/download/'+new_name, arcname = new_name) 
                        my_bar.progress(100, text=progress_text)
                        placeholder.empty()
                        st.success("Successfully downloaded!")
                        
                       
                    url_list_force = []
                    url_list_video = []
                    url_list_image = []
                    name_list_force = []
                    name_list_video = []
                    name_list_image = []
                    metadata = []
                    names_list = list(df_new[df_new['download'] == True]['objectname'])
                    for aa in find_result:
                        if aa['objectname'] in names_list:
                            metadata.append(aa)
                            if aa['datatype'] == 'Video':
                                url_list_video.append(aa['location'])
                                name_list_video.append(aa['objectname'])
                            if aa['datatype'] == 'Force':
                                url_list_force.append(aa['location'])
                                name_list_force.append(aa['objectname'])
                            if aa['datatype'] == 'Image':
                                url_list_image.append(aa['location'])
                                name_list_image.append(aa['objectname'])
                    select_df = pd.DataFrame(metadata)
                    remove_ll = ['user_access','location']
                    res = [i for i in list(select_df) if i not in list(remove_ll)]
                    select_df = select_df[res]
                    progress_text = "Operation in progress. Please wait."
                    placeholder = st.empty()
                    
                    my_bar = placeholder.progress(0, text=progress_text)
                    download_and_rename_videos(url_list_force, url_list_video, url_list_image, name_list_force,
                                           name_list_video,name_list_image, select_df, placeholder, my_bar,progress_text )
            
            if True in list(df_new['preview']):
                if np.sum(df_new['preview'] == True) == 1:
                    preview = st.button('preview selected')
                    if preview:
                        st.header(df_new[df_new['preview'] == True]['objectname'].to_string(index=False))
                        for aa in find_result:
                            names_list = list(df_new[df_new['preview'] == True]['objectname'])
                            if aa['objectname'] in names_list:
                                url_aa = aa['location']
                                if aa['datatype'] == 'Video':
                                    st.video(url_aa)
                                elif aa['datatype'] =='Image':
                                    print(url_aa)
                                    st.image(url_aa)
                                elif aa['datatype'] == 'Force':
                                    def my_plot(df1):
                                        import plotly.express as px
                                        melted_df = pd.melt(df1, id_vars = ['time'], var_name='Force', value_name='Value')
                                        fig = px.line(melted_df,x = 'time', y ='Value',color = 'Force')
                                        st.plotly_chart(fig, use_container_width=True)
            
                                    df1 = pd.DataFrame(json.loads(requests.get(url+aa['location']).text))
                                    my_plot(df1)
                                    st.table(df1)
                else:
                    st.error('You can only preview 1 file.')
        else:
            st.write('No raw data match.')              
