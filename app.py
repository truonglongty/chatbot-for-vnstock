import os
import google.generativeai as genai
import chromadb
import streamlit as st

from chromadb import Documents, EmbeddingFunction, Embeddings


os.environ["GEMINI_API_KEY"] = 'api-key here'

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable")
        genai.configure(api_key=gemini_api_key)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model,
                                   content=input,
                                   task_type="retrieval_document",
                                   title=title)["embedding"]


def load_chroma_collection(path, name):
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())

    return db


def get_relevant_passage(query, db, n_results):
  passage = db.query(query_texts=[query], n_results=n_results)['documents'][0]
  return passage


def make_rag_prompt(query, relevant_passage):
  escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = ("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the passage is irrelevant to the answer, you may ignore it.
  QUESTION: '{query}'
  PASSAGE: '{relevant_passage}'

  ANSWER:
  """).format(query=query, relevant_passage=escaped)

  return prompt


def generate_response(prompt):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    answer = model.generate_content(prompt)
    return answer.text


def generate_answer(db,query):
    #retrieve top 3 relevant text chunks
    relevant_text = get_relevant_passage(query,db,n_results=3)
    prompt = make_rag_prompt(query, 
                             relevant_passage="".join(relevant_text)) # joining the relevant chunks to create a single passage
    answer = generate_response(prompt)

    return answer


db=path=load_chroma_collection("my_vectordb", name="rag_experiment")


st.set_page_config(page_title="Chatbot for VN stock")

st.header("Gemini Application")

input=st.text_input("Input: ",key="input")

submit=st.button("Ask the question")

if submit:
    response=generate_answer(db, query=input)
    st.subheader("The Response is")
    st.write(response)