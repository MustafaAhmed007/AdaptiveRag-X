class MockGenerator:
    def generate(self,query,evidence):
        if not evidence:return 'I do not have enough evidence in the indexed knowledge to answer that reliably.'
        return 'Based on the retrieved evidence:\n\n'+'\n'.join(f'- {e.text}' for e in evidence[:3])
class ProviderGenerator:
    def __init__(self,client,model='gpt-4.1-mini'): self.client=client; self.model=model
    def generate(self,query,evidence):
        context='\n\n'.join(e.text for e in evidence)
        response=self.client.responses.create(model=self.model,input=f'Answer only from the evidence. Question: {query}\nEvidence:\n{context}')
        return response.output_text
