from torch import Tensor
from transformers import AutoTokenizer, AutoModel
from torch import no_grad
from typing import List

def average_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

tokenizer = AutoTokenizer.from_pretrained("Supabase/gte-small")
model = AutoModel.from_pretrained("Supabase/gte-small")
        
def generate_embeddings(prompt:str | List[str]) -> List[List[float]] | None:
    batch_dict = tokenizer(prompt, max_length=512, padding=True, truncation=True, return_tensors='pt')

    with no_grad():
        outputs = model(**batch_dict)
        embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
        
    return embeddings.tolist()