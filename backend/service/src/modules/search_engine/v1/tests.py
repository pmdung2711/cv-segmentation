from entity_search import EntityExtractor


sample = '''LANDCORP PROPERTY VIETNAM CO., LTD, Accountant.
2017 - 2019.
- In charge of periodic report of cash flow, budget and business KPIs.
- In charge of Tax reports and record accounting transactions.
- Process internal and external payments; transactions related to Banks and Tax department.
*Achivement : Build up data analyse as well as report forms, which is more time- saving , at the same time , provide more accurated periodic metrics of cash flow, and business KPIs.
'''

output = EntityExtractor.extract_entities_by_regex(sample)
print(output)