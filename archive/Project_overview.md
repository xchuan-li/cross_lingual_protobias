Topic 6: Cross-lingual prototypicality bias in multimodal AI evaluation (Subhadeep)

Description: Multimodal AI systems are increasingly used to evaluate how well images match text descriptions. However, these systems may rely not only on true semantic correctness, but also on what appears typical or stereotypical. For example, given the prompt “a doctor treating a patient,” a correct image might show a female doctor, while a more prototypical (but biased) image might show a male doctor. Similarly, for “a rich person,” models may prefer images reflecting stereotypical appearances rather than diverse or less typical ones.
In this project, we study whether such prototypicality bias is consistent across languages. Using a controlled dataset (ProtoBias) of image pairs (one semantically correct and one prototypical but incorrect), students will translate the same prompt into multiple languages and evaluate whether AI systems change their judgments depending on the language. This allows us to test whether models remain semantically grounded or rely on language- and culture-specific “typical” representations (RQ1).
Beyond this, the project will analyze whether cross-lingual differences are stronger in socially sensitive contexts (e.g., wealth, intelligence, profession) compared to neutral domains such as animals or objects (RQ2). This makes it possible to understand whether bias in AI systems is universal or shaped by linguistic and cultural variation.

AI relation: We will use multimodal large language models to evaluate image-text alignment under controlled multilingual conditions. By comparing model decisions across different languages for the same image pairs, the project investigates whether AI systems are robust to language variation or influenced by culturally specific prototypes.
Data: ProtoBias dataset (text prompts paired with two images: one semantically correct but less prototypical, and one more prototypical but incorrect). The same dataset will be reused, with the text prompts translated into multiple languages for cross-lingual evaluation. (I’ll provide the data)
Literature:
[1] https://aclanthology.org/2025.findings-acl.585/ 
[2] https://aclanthology.org/2024.emnlp-main.474/ 
[3] https://aclanthology.org/2022.gebnlp-1.9/ 
[4] https://aclanthology.org/2025.findings-emnlp.783/ 
[5] https://arxiv.org/abs/2601.04946 (ProtoBias)
