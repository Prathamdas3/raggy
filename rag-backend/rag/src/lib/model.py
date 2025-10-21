from langchain_huggingface.llms import HuggingFacePipeline
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
    # BitsAndBytesConfig,
)
import torch
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import os
from lib.logger import get_logger

load_dotenv()
logger= get_logger("lib/model")


MODEL_ID = os.getenv("MODEL_ID")
MODEL_PROMPT = """Read the following text carefully. Then create a simple summary. The summary should be very clear and easy for a dyslexic child to understand. Please use:

- Short sentences (no more than 10 words).
- Simple, everyday words (avoid hard or complex terms).
- Repetition of important ideas so they are remembered.
- Line breaks or bullet points to separate ideas.
- Explain in a friendly, calm, and supportive tone.

Text to summarize:
{context}

Now, write the summary as if you are explaining to a dyslexic child. End with a quick “big idea” sentence that reminds them what everything means in the simplest way possible.
"""

def get_chain():
    try:
        # Validate environment variables
        if not MODEL_ID:
            raise ValueError("SUMMARY_MODEL_ID environment variable not set")
        if not MODEL_PROMPT:
            raise ValueError("SUMMARY_MODEL_PROMPT environment variable not set")

        logger.info(f"Loading model: {MODEL_ID}")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

        # quantization_config = BitsAndBytesConfig(
        #     load_in_4bit=True,
        #     bnb_4bit_use_double_quant=True,
        #     bnb_4bit_quant_type="nf4",
        #     bnb_4bit_compute_dtype=torch.bfloat16,
        # )

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            # quantization_config=quantization_config,
            device_map="auto"
        )

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            temperature=0.3,
        )

        hf = HuggingFacePipeline(pipeline=pipe)
        prompt = PromptTemplate.from_template(MODEL_PROMPT)
        chain = create_stuff_documents_chain(llm=hf, prompt=prompt)

        logger.info("Model loaded and chain created successfully")
        return chain

    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        logger.error("Summary generation will not be available")
        return None
