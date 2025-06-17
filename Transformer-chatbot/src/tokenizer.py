import tensorflow_datasets as tfds

def load_tokenizer(questions, answers, vocab_size=2**13):
    tokenizer = tfds.deprecated.text.SubwordTextEncoder.build_from_corpus(
        questions + answers, target_vocab_size=vocab_size)
    return tokenizer
