Appendix: Review of Botan PR #5499
==================================

Note: Botan Release notes refer to this issue erroneously as `#5599`.

The following review in this section was entirely written by Anthropic's Fable 5 model. Please treat it with care as appropriate for AI generated content.

**"In TLS 1.3 require that the handshake is completed prior to application data"**

- **PR:** `randombit/botan#5499 <https://github.com/randombit/botan/pull/5499>`_
  (branch ``jack/tls13-app-data``)
- **Author:** Jack Lloyd — **Merged:** 2026-03-31 as ``d0c85903c``, 1 commit,
  +4/-0 in ``src/lib/tls/tls13/tls_channel_impl_13.cpp``
- **First released in:** Botan 3.11.1 (tagged 2026-03-31, two minutes after the
  merge — the patch release was evidently cut to ship this fix)
- **Scope:** TLS 1.3 record dispatch in ``Channel_Impl_13::from_peer``

The question examined here is whether this small change closes a real
vulnerability. The conclusion is that it does: before the fix, Botan's TLS 1.3
channel would deliver decrypted application data to the application *during*
the handshake, before the peer was authenticated.

The change
----------

The PR adds a single guard to the ``ApplicationData`` branch of the record
dispatch in ``Channel_Impl_13::from_peer``:

.. code-block:: cpp

   BOTAN_ASSERT_NONNULL(m_cipher_state);
   if(!m_cipher_state->can_decrypt_application_traffic()) {
      throw Unexpected_Message("Application data received before handshake completion");
   }

``Cipher_State::can_decrypt_application_traffic()`` returns true for a client
only in states ``ServerApplicationTraffic`` or ``Completed``, and for a server
only in state ``Completed``. The thrown ``Unexpected_Message`` is translated
into a fatal ``unexpected_message`` alert by the surrounding handler, which is
exactly the behavior RFC 8446 mandates for application data received at an
unexpected point.

Prior state of the code
-----------------------

In TLS 1.3 the record layer decrypts every incoming protected record with
whatever the *current* read key is; the true (inner) content type only becomes
visible after decryption. Botan's record layer
(``tls_record_layer_13.cpp``) faithfully implements this: it decrypts,
strips the padding, and hands the record with its inner type up to the channel.
The only pre-existing guard ("premature Application Data received") fired when
no cipher state existed at all, i.e. before the ServerHello was processed.

The channel's ``ApplicationData`` branch then passed the plaintext directly to
``callbacks().tls_record_received()`` with **no check of the handshake state**.
Consequently, in the entire window between ServerHello and handshake
completion, a record that decrypted correctly under the *handshake traffic
keys* with inner type ApplicationData was delivered to the application as
session data.

Vulnerability analysis
----------------------

Client side (the serious case)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After processing the ServerHello, the client's read key is derived from the
server handshake traffic secret. These keys derive purely from the (EC)DHE
exchange and are therefore shared with whoever performed that key exchange —
a party that is **not yet authenticated**. Authentication happens only when
CertificateVerify and Finished are validated later in the handshake.

An active man-in-the-middle who terminates the (EC)DHE toward the client thus
possesses the handshake traffic keys and can encrypt a record with inner type
ApplicationData. The AEAD verification in the record layer passes (the keys
are correct), and the pre-fix code handed the attacker's plaintext to the
application via ``tls_record_received``. The handshake subsequently fails —
the attacker cannot forge the server's CertificateVerify — but by then the
injection has already happened. This is a one-shot **unauthenticated data
injection** into the client application, attributed to a connection the
application believes it is making to the genuine server.

Server side
~~~~~~~~~~~

Symmetrically, a client could send application data under its handshake
traffic keys before sending its Finished message. The pre-fix server delivered
it. This matters most in deployments using client-certificate authentication:
the server application received data before the client's certificate and
Finished were verified — an authentication bypass for that data. Without
client authentication it remains a key-confirmation gap and a violation of
RFC 8446, which forbids application data prior to the Finished message.

Correct scoping of the fix
--------------------------

The guard does not reject any legitimate traffic. A client in state
``ServerApplicationTraffic`` — i.e. one that has processed the server's
Finished — may still accept application data. That is the legitimate 0.5-RTT
("early server data") case, and it is safe because the server's Finished is
processed only after its CertificateVerify, so the server is fully
authenticated at that point. The client transitions to ``Completed`` upon
sending its own Finished; the server accepts application data only once it has
processed the client's Finished. 0-RTT early data is not implemented by Botan's
server, so no legitimate pre-Finished data flow exists that the check could
break.

Severity assessment
-------------------

- The client-side attack requires an active on-path attacker; the server-side
  weakness is meaningful chiefly when client-certificate authentication is in
  use.
- Practical impact depends on application behavior: an application that waits
  for ``tls_session_activated`` before acting on received data is effectively
  immune. However, nothing in the callback API contract warns that
  ``tls_record_received`` could fire pre-authentication, so applications
  reasonably treat every delivery as authenticated peer data.
- No CVE was assigned. (The regression test for CVE-2026-35580 merged in the
  same window concerns an unrelated X.509 path-validation issue and should not
  be confused with this fix.)
- The flaw is of the same class as the historical "early application data"
  state-machine bugs (e.g. the SMACK family), which were treated as genuine
  vulnerabilities in other TLS stacks.

Verdict
-------

A real vulnerability, moderate severity: unauthenticated application-data
injection toward TLS 1.3 clients during the handshake window, and
pre-authentication data acceptance on servers (an authentication bypass for
that data where client certificates are used). The four-line fix closes it
cleanly by gating delivery of application data on the cipher state having
reached the application-traffic phase, matches RFC 8446's required alerting
behavior, and permits the legitimate 0.5-RTT case. The prompt 3.11.1 patch
release corroborates that upstream treated this as security-relevant despite
not assigning a CVE.
