import sys
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

print(f"Is CUDA available? {torch.cuda.is_available()}")
print(f"Device count: {torch.cuda.device_count()}")
print(f"Current device: {torch.cuda.current_device()}")
print(f"Device name: {torch.cuda.get_device_name(torch.cuda.current_device())}")

def generate_response(transcription):
    print("Loading tokenizer and model...")
    model_path = "./llama_model"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")
    print("Model and tokenizer loaded.")

    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    print("Pipeline created. Generating response...")
    
    # Generate a response
    response = generator(transcription, max_length=50, num_return_sequences=1)
    print("Response generated.")
    
    return response[0]['generated_text']

if __name__ == "__main__":
    transcription = sys.argv[1]
    response = generate_response(transcription)
    print(f"AI Response: {response}")
