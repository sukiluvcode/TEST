import pandas

df = pandas.read_json("crossref_nlo_doi.json")

def rename(row):
    row.title = row.title[0]
    return row.title
df.apply(rename, axis='columns')

pattern = r'\b(polymer(s)?|graphene)\b'
filtered_df = df[~df['title'].str.contains(pattern, case=False, regex=True)]
mask = filtered_df['title'].isin(['Issue Editorial Masthead', 'Issue Publication Information'])
filtered_df= filtered_df[~mask]
print(filtered_df)

filtered_df.DOI.to_csv('crossref_nlo_doi.csv', index=False)