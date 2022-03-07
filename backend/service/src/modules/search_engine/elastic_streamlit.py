from elasticsearch import Elasticsearch
import streamlit as st
import pandas as pd
import io

es = Elasticsearch(hosts='host.docker.internal', port=9200)
st.set_option('deprecation.showPyplotGlobalUse', False)
st.title(""" # INFOMATION SEARCHING - ELASTIC SEARCH - Tiếng Việt - Update""")

def find_phrase(index, input):
    query = {
        "from": 0,
        "query": {
            "match_phrase": {
                "description": {
                    index: {
                        "query": input
                    },
                }
            }
        }
    }
    res = es.search(index=index, body=query)
    resnum = res["hits"]["total"]["value"]
    for i in range(resnum):
        st.write(res["hits"]["hits"][i - 1]["_source"][index])

def find_all(index, input):
    query = {
        "from": 0,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        index: input
                    },
                }
            }
        }
    }
    res = es.search(index=index, body=query)
    resnum = res["hits"]["total"]["value"]
    new_query = create_standard_query(index, input, resnum)
    res2 = es.search(index=index, body=new_query)
    res_return = []
    for i in range(resnum):
        res_return.append(res2["hits"]["hits"][i - 1]["_source"][index])

    st.write(res_return)
    return res_return


def create_standard_query(index, input, num):
    query = {
        "from": 0,
        "size": num,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        index: input
                    },
                }
            }
        }
    }
    return query


def delete_index(name):
    index = es.indices.get_alias("*")
    for i in index.copy():
        if i[0] == ".":
            index.pop(i)
    if name in index:
        es.indices.delete(index=name)


def showall(index):
    es.indices.refresh(index)
    num = es.cat.count(index, params={"format": "json"})
    result = es.search(index=index, body={"from": 0, "size": num[0]["count"], "query": {"match_all": {}}})

    res = []
    if int(num[0]["count"]) < 2000:
        for i in range(len(result["hits"]["hits"])):
            res.append(result["hits"]["hits"][i]["_source"])
        df = pd.DataFrame(res)
        st.table(df)
    else:
        c = 0
        for i in range(len(result["hits"]["hits"])):
            res.append(result["hits"]["hits"][i]["_source"])
            c += 1
            if c == 2000:
                break
        df = pd.DataFrame(res)
        st.table(df)


def refreshindex():
    list = []
    for index in es.indices.get('*'):
        list.append(index)
    for i in list:
        if i[0] == ".":
            list.remove(i)
    list.sort()
    return list


def showindex(index):
    show = []
    for i in index:
        show.append(i)
    df = pd.DataFrame(show)
    st.table(df)


def search(index, query):
    res = es.search(index=index, body=query)
    # st.write(res)
    resnum = res["hits"]["total"]["value"]
    res_return = []
    if resnum == 0:
        st.write("No Result")
    else:
        if resnum <= choice:
            for i in range(resnum):
                st.write(res["hits"]["hits"][i - 1]["_source"])
                res_return.append(res["hits"]["hits"][i - 1]["_source"][index])
        else:
            for i in range(choice):
                st.write(res["hits"]["hits"][i - 1]["_source"])
                res_return.append(res["hits"]["hits"][i - 1]["_source"][index])

    st.write(res_return)
    return res_return

#that function still be in dev
def add_manual(index, input):
    doc = {}
    num = es.cat.count(index, params={"format": "json"})
    doc[index] = input
    es.index(index=index, doc_type=index, id=int(num[0]["count"]) + 1, document=doc)


if __name__ == "__main__":
    st.write("Please wait the elastic search service")

    while (es.ping() == False):
        es = Elasticsearch(hosts='localhost', port=9200)
    refreshindex()
    if es.ping():
        st.subheader("The elastic has been initiated")

        option = st.selectbox('Select mode: ', ('Search Engine', 'Database'))
        # st.write('You selected:', option)
        if option == 'Search Engine':
            st.write("This search engine will show out the name of companies, jobtitles and skills")
            input = st.text_input('Input', value="Please input something")
            choice = st.number_input("Number of result", 1, 30)

            index_list = refreshindex()
            index_input = st.selectbox('Index', options=index_list)
            query = create_standard_query(index_input, input, choice)

            if st.button('Searching'):
                search(index_input, query)
            if st.button('Searching all'):
                find_all(index_input, input)
            #if st.button('Add index'):
            #    delete_index(index_input, input)
            if st.button('Searching Matching'):
                find_all(index_input, input)


        elif option == 'Database':
            st.subheader("Manage Your Database")
            dbname = st.text_input('Database Name', value="")

            data_list = []
            upload_list = []
            info_doc = {}
            uploaded_file = st.file_uploader("Choose a file")
            if uploaded_file:
                for line in uploaded_file:
                    stringio = io.StringIO(line.decode("utf-8"))
                    string_data = stringio.read()
                    data_list.append(string_data)
                st.write("Finish Uploading")
            else:
                st.write("No File Found")

            if st.button('Upload Data to Elastic Search'):
                for i in data_list:
                    info_doc[str(dbname)] = i
                    upload_list.append(info_doc)
                    info_doc = {}
                for x in range(len(upload_list)):
                    es.index(index=dbname, doc_type=dbname, id=x, document=upload_list[x])
                data_list = []
                upload_list = []
                info_doc = {}
                st.write('Finish Uploading')

            if st.button('Delete Index in Elastic Search'):
                delete_index(dbname)

            st.subheader("List of indices")
            index = refreshindex()
            showindex(index)

            st.subheader("Element in index")
            index_input = st.selectbox('index', options=index)
            showall(index_input)

    else:
        st.write("Please running the elastic search service")
