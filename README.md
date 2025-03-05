# Model2Vec Inference module

🎯 Overview
-----------

This is the the inference container which can be used with Weaviate
`text2vec-transformers` module. You can download it directly from Dockerhub
using one of the pre-built images.

It is built to support only static (`model2vec`) models.

[Model2Vec](https://github.com/MinishLab/model2vec) models significantly
surpass other static embeddings models like GLoVe and BPEmb in performance,
and the pre-built Docker images containing these models are notably compact in size.

🐳 Pre-built images
-------------------

|Model Name|Image Name|
|---|---|
|`minishlab/potion-base-4M` ([Info](https://huggingface.co/minishlab/potion-base-4M))|`semitechnologies/model2vec-inference:minishlab-potion-base-4M`|
|`minishlab/potion-base-8M` ([Info](https://huggingface.co/minishlab/potion-base-8M))|`semitechnologies/model2vec-inference:minishlab-potion-base-8M`|
|`minishlab/potion-base-32M` ([Info](https://huggingface.co/minishlab/potion-base-32M))|`semitechnologies/model2vec-inference:minishlab-potion-base-32M`|

🔗 Useful Resources
--------------------

- [Locally Hosted Transformers Text Embeddings + Weaviate](https://weaviate.io/developers/weaviate/model-providers/transformers/embeddings)
- [Model2Vec](https://github.com/MinishLab/model2vec)
- [The Minish Lab](https://huggingface.co/minishlab)
