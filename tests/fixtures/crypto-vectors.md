---
schema: pdca.crypto-fixtures/v1
fixture_revision: '1'
example_only: true
execution_status: NOT_RUN
vectors:
- case_id: GCM-EMPTY
  mode: GCM
  key: '00000000000000000000000000000000'
  iv: '000000000000000000000000'
  aad: ''
  plaintext: ''
  ciphertext: ''
  tag: 58e2fccefa7e3061367f1d57a4e7455a
  source: NIST2007 / OpenSSL3.0.16 AES-GCM vectors
- case_id: GCM-BLOCK
  mode: GCM
  key: '00000000000000000000000000000000'
  iv: '000000000000000000000000'
  aad: ''
  plaintext: '00000000000000000000000000000000'
  ciphertext: 0388dace60b6a392f328c2b971b2fe78
  tag: ab6e47d42cec13bdf53a67b21257bddf
  source: OpenSSL3.0.16 AES-GCM vectors
- case_id: GCM-AAD-PARTIAL
  mode: GCM
  key: feffe9928665731c6d6a8f9467308308
  iv: cafebabefacedbaddecaf888
  aad: feedfacedeadbeeffeedfacedeadbeefabaddad2
  plaintext: d9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a721c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b39
  ciphertext: 42831ec2217774244b7221b784d0d49ce3aa212f2c02a4e035c17e2329aca12e21d514b25466931c7d8f6a5aac84aa051ba30b396a0aac973d58e091
  tag: 5bc94fbc3221a5db94fae95ae7121a47
  source: OpenSSL3.0.16 AES-GCM 60-byte/AAD vector
- case_id: GCM-IV8
  mode: GCM
  key: feffe9928665731c6d6a8f9467308308
  iv: cafebabefacedbad
  aad: feedfacedeadbeeffeedfacedeadbeefabaddad2
  plaintext: d9313225f88406e5a55909c5aff5269a86a7a9531534f7da2e4c303d8a318a721c3c0c95956809532fcf0e2449a6b525b16aedf5aa0de657ba637b39
  ciphertext: 61353b4c2806934a777ff51fa22a4755699b2a714fcdc6f83766e5f97b6c742373806900e49f24b22b097544d4896b424989b5e1ebac0f07c23f4598
  tag: 3612d2e79e3b0785561be14aaca2fccb
  source: OpenSSL3.0.16 AES-GCM non-96-bit-IV vector
- case_id: CCM-RFC1
  mode: CCM
  key: c0c1c2c3c4c5c6c7c8c9cacbcccdcecf
  iv: 00000003020100a0a1a2a3a4a5
  aad: '0001020304050607'
  plaintext: 08090a0b0c0d0e0f101112131415161718191a1b1c1d1e
  ciphertext: 588c979a61c663d2f066d0c2c0f989806d5f6b61dac384
  tag: 17e8d12cfdf926e0
  source: 'RFC3610 Packet Vector #1; M=8 L=2'
- case_id: XTS-TWO-BLOCKS
  mode: XTS
  key: '1111111111111111111111111111111122222222222222222222222222222222'
  iv: '33333333330000000000000000000000'
  aad: ''
  plaintext: '4444444444444444444444444444444444444444444444444444444444444444'
  ciphertext: c454185e6a16936e39334038acef838bfb186fff7480adc4289382ecd6d394f0
  source: OpenSSL3.0.16 / IEEE XTS example
- case_id: XTS-TAIL34
  mode: XTS
  key: fffefdfcfbfaf9f8f7f6f5f4f3f2f1f0bfbebdbcbbbab9b8b7b6b5b4b3b2b1b0
  iv: 9a785634120000000000000000000000
  aad: ''
  plaintext: 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2021
  ciphertext: edbf9dace45d6f6a7306e64be5dd824b9dc31efeb418c373ce073b66755529982538
  source: OpenSSL3.0.16 34-byte XTS reference vector
protocol_revision: 3.1.0
---

# 固定外部向量

十六进制均为原始字节，无隐式文本编码。expected ciphertext/tag在运行前从固定来源转录，不由待测实现产生。出处与核对范围见[来源](../sources.md)。XTS不含认证tag；CCM的ciphertext与tag分别列出。

实际运行独立保存actual和向量文件摘要。转录错误也必须作为失败排查，不能运行后悄悄改expected。本页NOT_RUN指未被真实节点任务采用，不阻止外部验证报告记录实际参考计算。
