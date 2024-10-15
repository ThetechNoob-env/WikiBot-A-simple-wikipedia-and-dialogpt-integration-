from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class DialogPTHandler:
    def __init__(self):
        # Use DialogPT model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialogPT-medium")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialogPT-medium")
        self.chat_history_ids = None

    def generate_response(self, user_input):
        input_ids = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors="pt")

        # Create attention mask
        attention_mask = torch.ones(input_ids.shape, device=input_ids.device)

        if self.chat_history_ids is not None:
            input_ids = torch.cat([self.chat_history_ids, input_ids], dim=-1)
            attention_mask = torch.cat([torch.ones(self.chat_history_ids.shape, device=input_ids.device), attention_mask], dim=-1)

        self.chat_history_ids = self.model.generate(input_ids, attention_mask=attention_mask, max_length=1000, pad_token_id=self.tokenizer.eos_token_id)
        response = self.tokenizer.decode(self.chat_history_ids[:, input_ids.shape[-1]:][0], skip_special_tokens=True)
        return response
