import tensorflow as tf
from src.mask_schedule import create_padding_mask, create_look_ahead_mask

# Positional Encoding
class PositionalEncoding(tf.keras.layers.Layer):
  def __init__(self, position, d_model, **kwargs): 
    super(PositionalEncoding, self).__init__(**kwargs)  
    self.pos_encoding = self.positional_encoding(position, d_model)

  def positional_encoding(self, position, d_model):
    angle_rads = self.get_angles(
        tf.range(position, dtype=tf.float32)[:, tf.newaxis],
        tf.range(d_model, dtype=tf.float32)[tf.newaxis, :],
        d_model)
    sines = tf.math.sin(angle_rads[:, 0::2])
    cosines = tf.math.cos(angle_rads[:, 1::2])
    pos_encoding = tf.concat([sines, cosines], axis=-1)
    return pos_encoding[tf.newaxis, ...]

  def get_angles(self, pos, i, d_model):
    angle_rates = 1 / tf.pow(10000, (2 * (i // 2)) / tf.cast(d_model, tf.float32))
    return pos * angle_rates

  def call(self, inputs, **kwargs):
    if isinstance(inputs, tf.SparseTensor):
        inputs = tf.sparse.to_dense(inputs)
    return inputs + self.pos_encoding[:, :tf.shape(inputs)[1], :]
  
  def compute_output_shape(self, input_shape):
    return input_shape

# Scaled Dot Product Attention
def scaled_dot_product_attention(query, key, value, mask):
  matmul_qk = tf.matmul(query, key, transpose_b=True)
  dk = tf.cast(tf.shape(key)[-1], tf.float32)
  scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)
  if mask is not None:
    scaled_attention_logits += (mask * -1e9)
  attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)
  output = tf.matmul(attention_weights, value)
  return output, attention_weights

# Multi-head Attention
class MultiHeadAttention(tf.keras.layers.Layer):
  def __init__(self, d_model, num_heads, **kwargs):  
    super(MultiHeadAttention, self).__init__(**kwargs)  
    assert d_model % num_heads == 0
    self.num_heads = num_heads
    self.d_model = d_model
    self.depth = d_model // num_heads

    self.wq = tf.keras.layers.Dense(d_model)
    self.wk = tf.keras.layers.Dense(d_model)
    self.wv = tf.keras.layers.Dense(d_model)
    self.dense = tf.keras.layers.Dense(d_model)
    
  def build(self, input_shape):
        # Keras가 자동으로 Dense 레이어의 build를 호출하므로 pass만 해도 무방
        super().build(input_shape)

  def split_heads(self, x, batch_size):
    x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
    return tf.transpose(x, perm=[0, 2, 1, 3])

  def call(self, v, k, q, mask):
    batch_size = tf.shape(q)[0]
    q = self.split_heads(self.wq(q), batch_size)
    k = self.split_heads(self.wk(k), batch_size)
    v = self.split_heads(self.wv(v), batch_size)
    scaled_attention, attention_weights = scaled_dot_product_attention(q, k, v, mask)
    scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])
    concat_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model))
    output = self.dense(concat_attention)
    return output

# Encoder Layer
def encoder_layer(d_model, num_heads, dff, rate=0.1):
  inputs = tf.keras.Input(shape=(None, d_model))
  padding_mask = tf.keras.Input(shape=(1, 1, None))

  attn_output = MultiHeadAttention(d_model, num_heads)(inputs, inputs, inputs, padding_mask)
  attn_output = tf.keras.layers.Dropout(rate)(attn_output)
  out1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)(inputs + attn_output)

  ffn_output = tf.keras.Sequential([
      tf.keras.layers.Dense(dff, activation='relu'),
      tf.keras.layers.Dense(d_model)
  ])(out1)
  ffn_output = tf.keras.layers.Dropout(rate)(ffn_output)
  out2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)(out1 + ffn_output)

  return tf.keras.Model(inputs=[inputs, padding_mask], outputs=out2)

# Decoder Layer
def decoder_layer(d_model, num_heads, dff, rate=0.1):
  inputs = tf.keras.Input(shape=(None, d_model))
  enc_output = tf.keras.Input(shape=(None, d_model))
  look_ahead_mask = tf.keras.Input(shape=(1, None, None))
  padding_mask = tf.keras.Input(shape=(1, 1, None))

  attn1 = MultiHeadAttention(d_model, num_heads)(inputs, inputs, inputs, look_ahead_mask)
  attn1 = tf.keras.layers.Dropout(rate)(attn1)
  out1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)(attn1 + inputs)

  attn2 = MultiHeadAttention(d_model, num_heads)(enc_output, enc_output, out1, padding_mask)
  attn2 = tf.keras.layers.Dropout(rate)(attn2)
  out2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)(attn2 + out1)

  ffn_output = tf.keras.Sequential([
      tf.keras.layers.Dense(dff, activation='relu'),
      tf.keras.layers.Dense(d_model)
  ])(out2)
  ffn_output = tf.keras.layers.Dropout(rate)(ffn_output)
  out3 = tf.keras.layers.LayerNormalization(epsilon=1e-6)(ffn_output + out2)

  return tf.keras.Model(inputs=[inputs, enc_output, look_ahead_mask, padding_mask], outputs=out3)

# Encoder
def encoder(*, vocab_size, num_layers, d_model, num_heads, dff, maximum_position_encoding, rate=0.1):
  inputs = tf.keras.Input(shape=(None,), dtype=tf.int32, name="inputs")
  padding_mask = tf.keras.Input(shape=(1, 1, None))
  x = tf.keras.layers.Embedding(vocab_size, d_model)(inputs)
  x *= tf.math.sqrt(tf.cast(d_model, tf.float32))
  x = PositionalEncoding(maximum_position_encoding, d_model)(x)
  x = tf.keras.layers.Dropout(rate)(x)

  for _ in range(num_layers):
    x = encoder_layer(d_model, num_heads, dff, rate)([x, padding_mask])

  return tf.keras.Model(inputs=[inputs, padding_mask], outputs=x)

# Decoder
def decoder(*, vocab_size, num_layers, d_model, num_heads, dff, maximum_position_encoding, rate=0.1):
  inputs = tf.keras.Input(shape=(None,), dtype=tf.int32, name="inputs")
  enc_output = tf.keras.Input(shape=(None, d_model))
  look_ahead_mask = tf.keras.Input(shape=(1, None, None))
  padding_mask = tf.keras.Input(shape=(1, 1, None))
  x = tf.keras.layers.Embedding(vocab_size, d_model)(inputs)
  x *= tf.math.sqrt(tf.cast(d_model, tf.float32))
  x = PositionalEncoding(maximum_position_encoding, d_model)(x)
  x = tf.keras.layers.Dropout(rate)(x)

  for _ in range(num_layers):
    x = decoder_layer(d_model, num_heads, dff, rate)([x, enc_output, look_ahead_mask, padding_mask])

  return tf.keras.Model(inputs=[inputs, enc_output, look_ahead_mask, padding_mask], outputs=x)

# Transformer
def transformer(vocab_size, num_layers, dff,
                d_model, num_heads, dropout,
                name="transformer"):

    # 인코더 입력
    inputs = tf.keras.Input(shape=(None,), dtype=tf.int32, name="inputs")
    # 디코더 입력
    dec_inputs = tf.keras.Input(shape=(None,), dtype=tf.int32, name="dec_inputs")

    # 마스크
    enc_padding_mask = tf.keras.layers.Lambda(
        create_padding_mask, output_shape=(1, 1, None),
        name='enc_padding_mask')(inputs)

    look_ahead_mask = tf.keras.layers.Lambda(
        create_look_ahead_mask, output_shape=(1, None, None),
        name='look_ahead_mask')(dec_inputs)

    dec_padding_mask = tf.keras.layers.Lambda(
        create_padding_mask, output_shape=(1, 1, None),
        name='dec_padding_mask')(inputs)

    # 인코더
    enc_outputs = encoder(
        vocab_size=vocab_size,
        num_layers=num_layers,
        dff=dff,
        d_model=d_model,
        num_heads=num_heads,
        rate=dropout,
        maximum_position_encoding=10000   # 최대 위치 인코딩
    )(inputs=[inputs, enc_padding_mask])

    # 디코더
    dec_outputs = decoder(
        vocab_size=vocab_size,
        num_layers=num_layers,
        dff=dff,
        d_model=d_model,
        num_heads=num_heads,
        rate=dropout,
        maximum_position_encoding=10000   # 최대 위치 인코딩
    )(inputs=[dec_inputs, enc_outputs, look_ahead_mask, dec_padding_mask])

    # 출력층
    outputs = tf.keras.layers.Dense(units=vocab_size, name="outputs")(dec_outputs)

    return tf.keras.Model(inputs=[inputs, dec_inputs], outputs=outputs, name=name)