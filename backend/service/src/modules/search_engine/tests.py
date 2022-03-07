from v1.elastic_search import ElasticSearch


if __name__ == "__main__":
    ElasticSearch.upload_database("programskill", "service/src/modules/search_engine/database/programskill.txt")
    ElasticSearch.upload_database("softskill", "service/src/modules/search_engine/database/softskill.txt")
    ElasticSearch.upload_database("languageskill", "service/src/modules/search_engine/database/language_skill.txt")
    ElasticSearch.upload_database("jobtitle", "service/src/modules/search_engine/database/linkedin_jobtitle.txt")