# Model2Vec Inference module

🎯 Overview
-----------

This is the the inference container modified from https://github.com/weaviate/t2v-model2vec-models, so that I could input and output embedding in an openai-compatible way (but not yet support upload in batch in single request).

It is built to support only static (`model2vec`) models.

[Model2Vec](https://github.com/MinishLab/model2vec) models significantly
surpass other static embeddings models like GLoVe and BPEmb in performance,
and the pre-built Docker images containing these models are notably compact in size.

🐳 Build your own image
--------------------------

- Build the docker container: `docker build -t potion-base-8m:latest . --build-arg MODEL_NAME=minishlab/potion-base-8M`

- Start the docker container: `docker run -p 8080:8080 potion-base-8m`

- Stop the running docker container: `docker stop <CONTAINER_NAME>`

🔗 Useful Resources
--------------------

- [Locally Hosted Transformers Text Embeddings + Weaviate](https://weaviate.io/developers/weaviate/model-providers/transformers/embeddings)
- [Model2Vec](https://github.com/MinishLab/model2vec)
- [The Minish Lab](https://huggingface.co/minishlab)
