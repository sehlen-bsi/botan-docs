Security and Vulnerabilities
============================

Botan |botan_version| fixed an issue in the Foreign Function Interface (FFI)
where ``botan_cipher_update()`` would create a verbatim copy of the input
buffer, into its output buffer for certain cipher modes. Affected were modes
that do not produce any encrypted output before all input data was processed,
namely SIV and CCM.

A typical user of ``botan_cipher_update()`` would assume that the output buffer
of this function is encrypted. This might result in an information disclosure,
if said output buffer was immediately shared with an untrusted party. Given that
the generated ciphertext is inconsistent, any decryption attempt would fail.
Also, the responsible code exists for many years. Therefore, we believe it to be
unlikely that this issue would affect any reasonable application without
detection during development and early testing.

See :ref:`changes/fixes` for additional details and a link to the patch.
