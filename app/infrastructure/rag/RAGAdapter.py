from app.core.ports.RAGPort import RAGPort

class RAGAdapter(RAGPort):

    def retrieve(self):
        print("retrieve")

    def generate(self):
        print(f"generate")