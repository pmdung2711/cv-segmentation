from elasticsearch import Elasticsearch
import io
import re
import streamlit as st

class ElasticSearch():

    @staticmethod
    def upload_database(dbname, database_path):
        es = Elasticsearch(hosts="localhost", port=9200)
        data_list = []
        upload_list = []
        info_doc = {}
        with open(database_path, "r") as f:
            data_list = [e.replace("\n", "") for e in f.readlines()]

        for i in data_list:
            info_doc[str(dbname)] = i
            upload_list.append(info_doc)
            info_doc = {}

        for x in range(len(upload_list)):
            es.index(index=dbname, id=x, document=upload_list[x])

    @staticmethod
    def delete_db(dbname):
        es = Elasticsearch(hosts="localhost", port=9200)
        index = es.indices.get_alias("*")
        for i in index.copy():
            if i[0] == ".":
                index.pop(i)
        if dbname in index:
            es.indices.delete(index=dbname)

    @staticmethod
    def treattext(input):
        return re.sub(r'[^\w\s]', '', input)

    @staticmethod
    def create_query_for_check(text, index="programskill"):
        query = {
            "from": 0,
            "query": {
                "match": {
                    index: {
                        "query": text,
                        "fuzziness": 0,
                        "operator": "or"
                    }
                }
            }
        }
        return query

    @staticmethod
    def create_query_withnum(text, num, index="programskill"):
        query = {
            "from": 0,
            "size": num,
            "query": {
                "match": {
                    index: {
                        "query": text,
                        "fuzziness": 0,
                        "operator": "or"
                    }
                }
            }
        }
        return query

    @staticmethod
    def search_func(es, query, text, index="programskill"):
        res_return = []
        res = es.search(index=index, body=query)
        resnum = res["hits"]["total"]

        if resnum == 0:
            return res_return
        else:
            new_query = ElasticSearch.create_query_withnum(text, resnum, index)
            res2 = es.search(index=index, body=new_query)
            # print(res2)
            for i in range(resnum):
                res_return.append(res2["hits"]["hits"][i]["_source"][index])
            return res_return

    # main_function
    # function return more than one
    @staticmethod
    def find_skill(input):
        es = Elasticsearch(hosts="localhost", port=9200)

        if es.ping():
            text = ElasticSearch.treattext(input)
            query = ElasticSearch.create_query_for_check(text)
            res = ElasticSearch.search_func(es, query, text)
            if res:
                return res
            else:
                return []
        else:
            return []

    # function return more than one
    @staticmethod
    def find_softskill(input):
        es = Elasticsearch()

        if es.ping():
            text = ElasticSearch.treattext(input)
            query = ElasticSearch.create_query_for_check(text, index="softskill")
            res = ElasticSearch.search_func(es, query, text, index="softskill")
            if res:
                return res
            else:
                return []
        else:
            return []

    # function return more than one
    @staticmethod
    def find_languageskill(input):
        es = Elasticsearch()
        if es.ping():
            text = ElasticSearch.treattext(input)
            query = ElasticSearch.create_query_for_check(text, index="languageskill")
            res = ElasticSearch.search_func(es, query, text, index="languageskill")
            if res:
                return res
            else:
                return []
        else:
            return []

    # function return more than one
    @staticmethod
    def find_jobtitle(input):
        es = Elasticsearch()

        if es.ping():
            text = ElasticSearch.treattext(input)
            query = ElasticSearch.create_query_for_check(text, index="jobtitle")
            res = ElasticSearch.search_func(es, query, text, index="jobtitle")
            if res:
                return res
            else:
                return []
        else:
            return []

    # function return more than one
    @staticmethod
    def find_company(input):
        es = Elasticsearch()

        if es.ping():
            text = ElasticSearch.treattext(input)
            query = ElasticSearch.create_query_for_check(text, index="company")
            res = ElasticSearch.search_func(es, query, text, index="company")
            if res:
                return res
            else:
                return []
        else:
            return []

    # function return one
    @staticmethod
    def find_university(input):
        es = Elasticsearch()
        if es.ping():
            text = ElasticSearch.treattext(input)
            query = ElasticSearch.create_query_withnum(text, num=1, index="university")
            res = es.search(index='university', body=query)
            if res["hits"]["total"]:
                return res["hits"]["hits"][0]['_source']['university']
            else:
                return []
        else:
            return []

    # function return one
    @staticmethod
    def find_degree(input):
        es = Elasticsearch()
        if es.ping():
            text = ElasticSearch.treattext(input)
            query = ElasticSearch.create_query_withnum(text, num=1, index="degree")
            res = es.search(index='degree', body=query)
            if res["hits"]["total"]:
                return res["hits"]["hits"][0]['_source']['university']
            else:
                return []
        else:
            return []

        # Get skill by ElasticSearch

    @staticmethod
    def get_skill(text):
        res = ElasticSearch.find_skill(text)
        return [e.replace("\n", "") for e in res]

    # Get soft skill by ElasticSearch
    @staticmethod
    def get_softskill(text):
        res = ElasticSearch.find_softskill(text)
        return [e.replace("\n", "") for e in res]

    # Get soft skill by ElasticSearch
    @staticmethod
    def get_languageskill(text):
        res = ElasticSearch.find_languageskill(text)
        return [e.replace("\n", "") for e in res]

    # Get job title by ElasticSearch
    @staticmethod
    def get_jobtitle(text):
        res = ElasticSearch.find_jobtitle(text)
        return [e.replace("\n", "") for e in res]

    # Get company name by ElasticSearch
    @staticmethod
    def get_company(text):
        res = ElasticSearch.find_company(text)
        return [e.replace("\n", "") for e in res]

        # Get University name by ElasticSearch

    @staticmethod
    def get_university(text):
        res = ElasticSearch.find_university(text)
        return [e.replace("\n", "") for e in res]

    # Get University name by ElasticSearch
    @staticmethod
    def get_degree(text):
        res = ElasticSearch.find_degree(text)
        return [e.replace("\n", "") for e in res]

