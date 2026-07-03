#!/usr/bin/env bash
# exit on error
set -o errexit

# Install the explicit requirements using standard pip
pip install qdrant-client sentence-transformers langchain-text-splitters pypdf langchain-core langchain-community fastapi uvicorn requests rank_bm25 openai python-dotenv
