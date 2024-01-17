import streamlit as st
import requests
import json
import pandas as pd
url = 'https://raw-data-mart-default-rtdb.firebaseio.com/'
st.set_page_config(page_title="“Will Call” Raw Data Mart", page_icon=":floppy_disk:", layout="wide")
st.title('Data Management')

if not 'info_user' in st.session_state:
    st.header('💁 Your session has expired.')
    st.write('Your session ended. Please sign in again.')
    st.image('https://cdn.dribbble.com/users/1150186/screenshots/6290394/session_timeout_warning.jpg',width=400)
else:
    if (st.session_state['info_user']['permission'][2] == '0'):
        st.header('💁 Forbidden')
        st.write('You don\'t have permission to access this resource. Please ask for permission to access.')
        import random
        random_number = random.randint(0, 2)
        urls = ['https://http.dog/403.jpg','https://httpcats.com/403.jpg','https://http.garden/403.jpg']
        st.image(urls[random_number],width=400)
    else:
        
        if not "flag" in st.session_state:
            st.session_state["flag"] = ''
        
        if st.session_state["flag"] == 1:
            st.success('Delete collection successful!')
            st.session_state["flag"] = ''
        
        
        
        st.header('Current collection table')
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
        
        table = json.loads(requests.get(url+'object.json?orderBy="delete"&endAt=0').text)
        if type(table) == dict:
            table_list = []
            for v in table.values():
                table_list.append(v)
        elif type(table) == list:
                table_list = table
        df = pd.DataFrame(table_list)
        df = df[['collectionid','collectiontype','group','participant','birthdate','date','created',]]
        df = df.loc[df.astype(str).drop_duplicates().index]
        df.columns = ['collection id','collection type','group','participant','birthdate','collect date','create date']
        print(df)
        selection = aggrid_interactive_table(df=df)
            
        tab1, tab2, tab3, tab4, tab5= st.tabs(["Collection Detail", "View Collection Log", "Delete Collection", "Add New Tags", "Update Existing Tags"])
        
        with tab1:
            # detail
            if selection.selected_rows != []:
                select_collectionid = pd.DataFrame(selection["selected_rows"])['collection id'][0]
                info_select = json.loads(requests.get(url + 'object.json?orderBy="collectionid"&equalTo="'+select_collectionid+'"').text)
                for i in info_select.values():
                    with st.expander(i['objectname']):
                        for keys in ['location','user_access']:
                            i.pop(keys) 
                        st.dataframe(pd.DataFrame.from_dict(i,orient = 'index', columns = ['Information']),use_container_width=True)
            else:
                st.write("Please select a collection to see detail.")
        
        with tab2:
            # View Data Log
            if selection.selected_rows != []:
                select_collectionid = pd.DataFrame(selection["selected_rows"])['collection id'][0]
                info_select = json.loads(requests.get(url + 'object.json?orderBy="collectionid"&equalTo="'+select_collectionid+'"').text)
                for i in info_select.values():
                    with st.expander(i['objectname']):
                        user_access = pd.DataFrame.from_dict(i['user_access'])[['time','username','action','success']]
                        user_access.columns = ['time','username','action','success']
                        aggrid_interactive_table(df=user_access)
            else:
                st.write("Please select a collection to see detail.")
                
        with tab3:
            # delete collection
            if selection.selected_rows != []:
                select_collectionid = pd.DataFrame(selection["selected_rows"])['collection id'][0]
                expander = st.expander('You are deleting the collection with id: {}.'.format(select_collectionid))
                info_select = json.loads(requests.get(url + 'object.json?orderBy="collectionid"&equalTo="'+select_collectionid+'"').text)
                objects = [i['objectname'] for i in info_select.values()]
                if len(objects) <= 1:
                    expander.write('{} object belongs to this collection:\n{}'.format(len(objects),objects))
                else:
                    expander.write('{} objects belong to this collection:\n{}'.format(len(objects),objects))
                
                delete = st.text_input('To confirm deletion, type permanently delete in the text input field and enter.',placeholder = 'permanently delete')
                if delete == 'permanently delete':
                    for k,v in info_select.items():
                        requests.put(url +'object/'+ k +'/delete.json', "1")
                    st.session_state["flag"] = 1
                    st.experimental_rerun()
                
            else:
                st.write("Please select a collection first.")
        with tab4:
            # Add new tags
            if selection.selected_rows != []:
                select_collectionid = pd.DataFrame(selection["selected_rows"])['collection id'][0]
                info_select = json.loads(requests.get(url + 'object.json?orderBy="collectionid"&equalTo="'+select_collectionid+'"').text)
                objects = [i['objectname'] for i in info_select.values()]
                choice = st.multiselect('object', objects,[])
                if choice != []:
                    with st.form('Add new tag'):
                        col1, col2 = st.columns(2)
                        with col1:
                            tag_name = st.text_input('Tag Name:')
                        with col2:
                            tag_value = st.text_input('Tag Value:')
                        submit_add = st.form_submit_button("Add new element to all selected objects")
                    if submit_add:
                        if (tag_name!='') and (tag_value!=''):
                            for k,v in info_select.items():
                                if v['objectname'] in choice:
                                    requests.put(url + 'object/' +k+'/'+tag_name+'.json',json = tag_value)
                                    st.success("Add new tag successful!")
            else:
                st.write("Please select a collection first.")
                
        with tab5:
            cannot_change_tag = ['location','user_access','group','birthdate','collectionid',
                                 'collectiontype','created','datatype','date','modified',
                                 'participant','participantid','sex']
            # Update existing tags
            if selection.selected_rows != []:
                select_collectionid = pd.DataFrame(selection["selected_rows"])['collection id'][0]
                info_select = json.loads(requests.get(url + 'object.json?orderBy="collectionid"&equalTo="'+select_collectionid+'"').text)
                objects = [i['objectname'] for i in info_select.values()]
                objects.insert(0,'')
                choice = st.selectbox('object', objects)
                if choice != '':
                    st.info('Please add, update, delete tags by modify rows directly.')
                    for k, v in info_select.items():
                        if v['objectname'] == choice:
                            object_key = k
                            save_change = {}
                            for x in cannot_change_tag :
                                save_change[x] = v[x]
                            for keys in cannot_change_tag :
                                v.pop(keys)
                            df = pd.DataFrame.from_dict(v,orient = 'index', columns = ['Tag Value'])
                            edit_df = st.experimental_data_editor(df,use_container_width=True, num_rows = 'dynamic')
                            change = list(edit_df.T.to_dict(orient = 'index').values())[0]
                            for x in cannot_change_tag:
                                change[x] = save_change[x]
                            
                    saved = st.button('Save the changes')
                    if saved:
                        from datetime import datetime
                        now = str(datetime.now())[:19]
                        change['modified'] = now
                        change['user_access'].append({"action":"modify","success":1,"time":now,"username":st.session_state['info_user']['name']})
                        requests.put(url + 'object/' + object_key +'.json' ,json = change)
                        st.success("Save changes successful!")
                            #requests.put()
            else:
                st.write("Please select a collection first.")
        
    
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
