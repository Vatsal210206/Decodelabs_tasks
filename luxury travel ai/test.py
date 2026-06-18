import google.generativeai as genai

genai.configure(api_key="AIzaSyCQ6qrnNvOIvNrBJhv2EhfSE76on8oeW2Q")

for m in genai.list_models():
    print(m.name)