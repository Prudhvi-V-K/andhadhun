from google.genai import types
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

class LangChain:
    def __init__(self, doc):
        self.raw_documents = TextLoader(doc).load()
        self.text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0, separator="\n")
        self.documents = self.text_splitter.split_documents(self.raw_documents)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key="AIzaSyAZNnXBDZGg58ocXdOP7VqmC3thKaqV3VE")
        self.vecstore = Chroma.from_documents(
            self.documents,
            embedding=self.embeddings)
        self.retriever = self.vecstore.as_retriever()

        self.template = """You are an assistant to a blind person. Your task is to provide accurate and relevant descriptions of what is happening in an image given to you. Omit irrelevant descriptions that a blind person would not understand, such as color. Also assume that the person knows the context of what is happening, such as being indoors.\n\n*Instructions:*\n\n1.  *Object Detection:* Identify all prominent objects present in the image.  Focus on concrete, recognizable objects.  Avoid abstract interpretations.\n2.  *Object Listing:* Create a list of the identified objects.  Use concise, single-word labels for each object (e.g., "dog", "car", "building", "tree", "person").\n3.  *Object Description:* Provide a short, descriptive sentence for each object identified in the "objects" list.  Include relevant details such as:\n    *   Appearance (color, size, shape)\n    *   Any immediately apparent attributes (e.g., "running", "parked", "smiling").\n    *   Contextual information that is directly observable from the image and helps differentiate the object.\n4.  *General Description:* Offer a brief (1-2 sentence) overview of the overall scene depicted in the image. This description should capture the general atmosphere, setting, and any apparent relationships between the objects.\n5.  *JSON Formatting:*  Your output MUST be a valid JSON object conforming to the following schema:\n\n\n{\n    "objects": ["object1", "object2", ...],\n    "obj_description": {\n        "object1": "Description of object1.",\n        "object2": "Description of object2.",\n        ...\n    },\n    "general_description": "A brief description of the overall scene."\n}',)"""

    def get_prompt(self, cache):
        cache_join = ",".join(cache)
        return self.template + "This is the previous responses to the images: " + cache_join

    def generate_response(self, client,prompt, file, system_instruction):
        return client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt, file],
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=1,
                        response_mime_type="application/json",
                    ),
                )

    def get_response(self):
        prompt = self.get_prompt()
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key="AIzaSyBAwAwPzjetIm_q9vvEh_rXpfQbMnLxzVk")

        return llm.send(prompt)
