from transformers import pipeline

summarizer = pipeline("text-generation", model="facebook/bart-large-cnn")